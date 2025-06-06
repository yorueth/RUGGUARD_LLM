# Project RUGGUARD: LLM-Powered Trustworthiness Bot
This repository contains the source code for the Project RUGGUARD X (Twitter) Bot, now enhanced with Google's Gemini 1.5 Flash AI model. This advanced version moves beyond simple metrics to provide intelligent, qualitative analysis of user accounts on demand.

The bot's goal is to offer deeper insights into an account's behavior by leveraging a Large Language Model (LLM) to analyze their bio and recent tweets for sentiment, topics, and potential red flags.

# ✨ Key Features
On-Demand Trigger: Summon the bot by replying to any tweet with the phrase @projectruggaurd riddle me this.

LLM-Powered Intelligent Analysis: Instead of a simple score, the bot uses the Gemini 1.5 Flash model to generate a nuanced, human-like summary of a user's profile, bio, and recent tweets.

Qualitative Insights: The AI looks for sentiment, spammy language, bot-like activity, or genuine project focus, providing a much deeper analysis than metrics alone.

Targeted Reporting: The bot correctly analyzes the author of the original tweet, not the user who triggered the command.

Customizable "Brain": The analysis prompt sent to the LLM is easily editable within the main.py file, allowing you to change the bot's analytical focus and personality.

# 🤖 New Architecture: The LLM Workflow
The integration of an LLM fundamentally changes how the bot operates. The new workflow is as follows:

Trigger : A user on X replies to a tweet with the bot's trigger phrase.

Data Aggregation (X API): The bot is activated and collects two types of data on the original tweeter:

Quantitative Data : Account age, follower/following count, verification status, etc.

Qualitative Data : The user's bio and their 5 most recent original tweets.

LLM Synthesis (Google AI API) : All the collected data is packaged into a detailed prompt. This prompt is then sent to the Gemini 1.5 Flash model via the Google AI API.

Report Generation: Gemini processes the entire context and generates a concise summary paragraph and a final "Trust Signal" rating (e.g., Positive, Neutral, Caution).

Reply (X API) : The bot takes the clean text from Gemini and posts it as a reply to the user who initiated the request.

# ⚙️ Setup and Installation
The setup process now requires an additional API key from Google.

1. Prerequisites
An X Developer Account with an App inside a Project.
A Google AI API Key. You can get one for free from the Google AI Studio.

3. Project Files
In your Replit workspace, you will need two files:

main.py : The complete Python script for the bot.
requirements.txt: The list of necessary Python libraries.
Create these files and copy the contents from the previous response.

3. Install Dependencies
Once the requirements.txt file is created, Replit will usually prompt you to install the dependencies. If not, open the Shell tab and run the following command:

Bash

pip install -r requirements.txt

4. API Key Configuration (Crucial)
This bot requires 6 API keys in total to function. These must be stored securely using Replit's Secrets tool.

In your Replit project, open the Secrets tab (padlock icon 🔒).

Add the following 6 secrets one by one. The key names must be an exact match.

X (Twitter) Keys (5 total):

X_API_KEY
X_API_KEY_SECRET
X_ACCESS_TOKEN
X_ACCESS_TOKEN_SECRET
X_BEARER_TOKEN
Google AI Key (1 total):

GOOGLE_API_KEY

# ▶️ How to Run the Bot
Run the Project: After setting up the files and secrets, simply press the main "Run" button at the top of your Replit workspace. The console should display status messages indicating that the X and Google AI clients have been initialized successfully.

Deploy for 24/7 Uptime : To ensure the bot is always online and listening for triggers, you must deploy it.

Click the "Deploy" button in the top-right corner of the workspace.
Choose the "Worker" deployment type, as the bot is a background process that does not need a web page.
Follow the on-screen steps to launch your permanent deployment.

# 🧠 Customizing the Analysis
The core intelligence of this bot lies in the prompt variable inside the get_llm_analysis function in main.py.

Python

def get_llm_analysis(user_data: dict) -> str:
    """
    Sends user data to the Gemini LLM for analysis and returns its summary.
    """
    # --- This prompt is the "brain" of your bot. Customize it to change the analysis. ---
    prompt = f"""
    You are an expert crypto project analyst...
    ...
    """
By editing the text within this prompt, you can change the bot's personality, its analytical focus (e.g., focus more on sentiment, or on specific keywords), and the format of its output. Experiment with this prompt to fine-tune the bot's performance.
