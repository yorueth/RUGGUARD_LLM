# main.py - Project RUGGUARD // LLM-POWERED ANALYSIS BOT

import os
import tweepy
import google.generativeai as genai
from datetime import datetime, timezone
from dotenv import load_dotenv

# ==============================================================================
# 1. CONFIGURATION & CLIENT INITIALIZATION
# ==============================================================================
load_dotenv()

# --- Load API keys from environment ---
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
X_API_KEY = os.getenv("X_API_KEY")
X_API_KEY_SECRET = os.getenv("X_API_KEY_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- Validate that all keys are present ---
if not all([X_BEARER_TOKEN, X_API_KEY, X_API_KEY_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET, GOOGLE_API_KEY]):
    raise ValueError("FATAL ERROR: All 6 API keys (5 for X, 1 for Google) must be set in Replit Secrets or .env file.")

# --- Configure clients ---
try:
    x_client = tweepy.Client(
        bearer_token=X_BEARER_TOKEN, consumer_key=X_API_KEY,
        consumer_secret=X_API_KEY_SECRET, access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET, wait_on_rate_limit=True
    )
    genai.configure(api_key=GOOGLE_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
    print("INFO: X and Google AI clients configured successfully.")
except Exception as e:
    raise ConnectionError(f"Failed to initialize API clients: {e}")

# --- Bot Settings ---
BOT_USERNAME = "projectruggaurd"
TRIGGER_PHRASE = "riddle me this"


# ==============================================================================
# 2. CORE LOGIC: DATA GATHERING & LLM ANALYSIS
# ==============================================================================

def get_llm_analysis(user_data: dict) -> str:
    """
    Sends user data to the Gemini LLM for analysis and returns its summary.
    """
    # --- This prompt is the "brain" of your bot. Customize it to change the analysis. ---
    prompt = f"""
    You are an expert crypto project analyst specializing in social media presence on X (formerly Twitter).
    Your task is to provide a concise, neutral trustworthiness analysis of a user based on the data provided.
    Focus on identifying potential red flags (e.g., spam, engagement farming, suspicious language) or positive signals (e.g., genuine interaction, clear project focus).

    **Data for User @{user_data['username']}:**
    - **Account Age:** {user_data['age_days']} days (Created: {user_data['created_at']})
    - **Follower Count:** {user_data['followers']}
    - **Following Count:** {user_data['following']}
    - **Follower/Following Ratio:** {user_data['follower_ratio']}
    - **X Verified Status:** {'Yes' if user_data['is_verified'] else 'No'}
    - **User Bio:** "{user_data['bio']}"
    - **Recent Tweets:**
    {user_data['recent_tweets']}

    **Instructions:**
    1. Write a one-paragraph summary of your findings.
    2. Conclude with a final "Trust Signal" on a new line. The signal must be one of: Positive, Neutral, Caution, or Red Flag.
    3. Your entire response should only be the summary paragraph and the Trust Signal line. Do not be conversational.
    """
    
    try:
        print(f"INFO: Sending data for @{user_data['username']} to Gemini API...")
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"ERROR: Gemini API call failed: {e}")
        return "LLM analysis could not be performed due to an API error."

def get_user_data_and_analyze(user_id: str) -> str:
    """
    Gathers all data from X for a user, then passes it to the LLM for analysis.
    """
    print(f"INFO: Starting data collection for user ID: {user_id}")
    try:
        # --- Get user profile data ---
        user_response = x_client.get_user(
            id=user_id,
            user_fields=["created_at", "description", "public_metrics", "verified"]
        )
        if not user_response.data: return "Analysis Failed: User not found."
        user = user_response.data
        
        # --- Get user's recent tweets ---
        tweets_response = x_client.get_users_tweets(id=user_id, max_results=5, exclude=["retweets", "replies"])
        recent_tweets_text = "\n".join([f"- '{tweet.text}'" for tweet in tweets_response.data]) if tweets_response.data else "No recent tweets found."

        # --- Compile all data into a dictionary ---
        metrics = user.public_metrics
        follower_ratio = metrics['followers_count'] / metrics['following_count'] if metrics['following_count'] > 0 else 0
        
        compiled_data = {
            "username": user.username,
            "age_days": (datetime.now(timezone.utc) - user.created_at).days,
            "created_at": user.created_at.strftime('%b %Y'),
            "followers": metrics['followers_count'],
            "following": metrics['following_count'],
            "follower_ratio": round(follower_ratio, 2),
            "is_verified": user.verified,
            "bio": user.description or "Not provided.",
            "recent_tweets": recent_tweets_text
        }

        # --- Send the compiled data for LLM analysis ---
        llm_summary = get_llm_analysis(compiled_data)
        
        # --- Format the final reply ---
        return (
            f"🤖 LLM-Powered Analysis for @{user.username}\n"
            f"-----------------------------------\n"
            f"{llm_summary}\n"
            f"-----------------------------------\n"
            f"Analyzed by #ProjectRUGGUARD w/ Gemini 1.5 Flash"
        )
        
    except Exception as e:
        print(f"ERROR: An error occurred during data collection for user {user_id}: {e}")
        return "Analysis Failed: Could not retrieve complete user data from X."

# ==============================================================================
# 3. X API STREAM LISTENER
# ==============================================================================
class BotStreamListener(tweepy.StreamingClient):
    """Monitors the X stream and triggers the analysis workflow."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("INFO: Listener active, monitoring X stream...")

    def on_tweet(self, tweet: tweepy.Tweet):
        is_reply = tweet.referenced_tweets and tweet.referenced_tweets[0].type == 'replied_to'
        if is_reply and TRIGGER_PHRASE.lower() in tweet.text.lower():
            print(f"INFO: Trigger detected in tweet {tweet.id}. Initiating analysis.")
            try:
                original_tweet_id = tweet.referenced_tweets[0].id
                target_user_id = x_client.get_tweet(original_tweet_id, expansions=["author_id"]).data.author_id

                if target_user_id:
                    final_report = get_user_data_and_analyze(target_user_id)
                    x_client.create_tweet(text=final_report, in_reply_to_tweet_id=tweet.id)
                    print(f"INFO: Reply sent successfully for tweet {tweet.id}.")
                else:
                    raise Exception("Original author ID not found.")
            except Exception as e:
                print(f"ERROR: Failed to process trigger for tweet {tweet.id}: {e}")

    def on_error(self, status):
        print(f"ERROR: Stream error with status code: {status}")


# ==============================================================================
# 4. MAIN EXECUTION BLOCK
# ==============================================================================
if __name__ == "__main__":
    print("INFO: Initializing LLM-Powered RUGGUARD Bot...")
    listener = BotStreamListener(bearer_token=X_BEARER_TOKEN)
    
    # Reset stream rules to ensure a clean state
    if rules := listener.get_rules().data:
        listener.delete_rules([rule.id for rule in rules])
        print("INFO: Old stream rules cleared.")
        
    rule = f"@{BOT_USERNAME} {TRIGGER_PHRASE}"
    listener.add_rules(tweepy.StreamRule(rule))
    print(f"INFO: Stream rule set: '{rule}'")
    
    listener.filter(expansions=["author_id"], tweet_fields=["referenced_tweets"])