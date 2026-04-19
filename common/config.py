import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "AI")

# Mapping 'natural' user names to real Account IDs
# Since you are on free tier, map "me" or "dev1" to your own email/account ID
USER_MAP = {
    "dev1": JIRA_EMAIL, 
    "me": JIRA_EMAIL,
    "qa": JIRA_EMAIL
}