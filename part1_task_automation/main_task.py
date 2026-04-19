# import sys
# import os
# # Add project root to python path so we can import 'common'
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from common.jira_client import JiraManager
# from common.config import PROJECT_KEY, USER_MAP
# from part1_task_automation.nlp_processor import CommandParser

# def main():
#     print("🟦 JIRA TASK AUTOMATION STARTED")
#     print("Try: 'Create a high priority bug called \"Login Error\" assign to dev1'")
    
#     jira = JiraManager()
#     parser = CommandParser()

#     while True:
#         command = input("\nEnter Command (or 'exit'): ")
#         if command == "exit": break

#         intent, params = parser.parse(command)
#         print(f"DEBUG: Intent={intent}, Params={params}")

#         try:
#             if intent == "create_issue":
#                 summary = params.get('content', 'New Issue')
#                 assignee_alias = params.get('assignee')
#                 assignee_email = USER_MAP.get(assignee_alias) # Map 'dev1' to email
                
#                 key = jira.create_issue(
#                     project=PROJECT_KEY, 
#                     summary=summary, 
#                     issue_type=params.get('type', 'Task'), 
#                     priority=params.get('priority', 'Medium'),
#                     assignee=assignee_email
#                 )
#                 print(f"✅ Created {key}: {summary}")

#             elif intent == "move_issue":
#                 key = params.get('issue_key')
#                 status = params.get('target_status')
#                 if key and status:
#                     success = jira.transition_issue(key, status)
#                     if success: print(f"✅ Moved {key} to {status}")
#                     else: print(f"❌ Failed to move {key} (Check workflow setup)")
#                 else:
#                     print("❌ Missing Issue Key or Target Status")

#             elif intent == "add_comment":
#                 key = params.get('issue_key')
#                 content = params.get('content')
#                 if key and content:
#                     jira.add_comment(key, content)
#                     print(f"✅ Comment added to {key}")
#                 else:
#                     print("❌ Missing Key or Comment text")
            
#             else:
#                 print("⚠️  I didn't understand that command.")

#         except Exception as e:
#             print(f"❌ Error: {e}")

# if __name__ == "__main__":
#     main()


import sys
import os
import requests
from requests.auth import HTTPBasicAuth

# 1. FIX PATH: Add the project root to system path so we can find 'common'
# This must happen BEFORE other imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from google import genai

# 2. FIX IMPORT: Import directly from the sibling file 'tools.py'
from tools import jira_tools 
from google.genai import types

load_dotenv(
    dotenv_path=os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", ".env")
    ),
    override=True
)


print("DEBUG KEY:", os.getenv("GEMINI_API_KEY"))


# ✅ NEW: Create Gemini client (replaces deprecated configure())
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# SYSTEM PROMPT: Zero Definitions. Pure Intelligence.
# SYSTEM_PROMPT = f"""
# You are an advanced Jira Autonomous Agent. 
# You have permission to access the ENTIRE Jira Cloud REST API via the 'execute_jira_api' tool.

# YOUR INSTRUCTIONS:
# 1. You are NOT limited to specific tasks. You can do anything the Jira API allows (Create, Search, Delete, Comment, Link, Assign, Sprint management, etc.).
# 2. You must use your internal knowledge of the 'Atlassian Jira Cloud REST API v3' to construct the correct URL endpoints and JSON payloads.
# 3. Always use the project key '{os.getenv("JIRA_PROJECT_KEY")}' when context is needed.
# 4. If a user asks for something complex (e.g., "Find who is overloaded"), break it down:
#    - Step 1: Search for issues assigned to users.
#    - Step 2: Count them in your head.
#    - Step 3: Report the result.

# GOAL: Solve the user's request by any means necessary using the API.
# """

def get_my_account_id():
    url = f"{os.getenv('JIRA_URL')}/rest/api/3/myself"
    auth = HTTPBasicAuth(os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN'))
    try:
        r = requests.get(url, headers={"Accept": "application/json"}, auth=auth)
        return r.json().get('accountId')
    except:
        return "unknown"

my_id = get_my_account_id()

# --- UPDATED SYSTEM PROMPT ---
SYSTEM_PROMPT = f"""
You are an advanced Jira Autonomous Agent. 
You have permission to access the ENTIRE Jira Cloud REST API via the 'execute_jira_api' tool.

YOUR KNOWLEDGE BASE (CRITICAL):
1. **Find User IDs**: To find a user by name (e.g. "Dev1", "Sarah"), you MUST use:
   `GET /rest/api/3/user/search?query=Name`
   *Never guess an Account ID. Always search first.*
   
2. **Assigning Issues**: When creating or editing, use the 'assignee' field:
   `"assignee": {{ "id": "ACCOUNT_ID_FROM_SEARCH_STEP" }}`

3. **Me**: If the user says "me", use Account ID: "{my_id}"

4. **Project Key**: Always use '{os.getenv("JIRA_PROJECT_KEY")}'.

STRATEGY FOR ASSIGNMENT:
If the user says "Create bug and assign to Sarah":
   Step 1. Call `execute_jira_api("GET", "/rest/api/3/user/search?query=Sarah")`
   Step 2. Read the JSON response to find Sarah's "accountId".
   Step 3. Call `execute_jira_api("POST", "/rest/api/2/issue", ...)` using that ID.

GOAL: Solve the user's request by any means necessary.
"""

MODEL_NAME = "gemini-2.5-flash"

def main():
    print("🟥 JIRA GOD MODE ACTIVATED")
    print("The AI now has full control over the REST API. Be careful.")

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[
                    SYSTEM_PROMPT,
                    user_input
                ],
                config=types.GenerateContentConfig(
                    tools=jira_tools
                )
            )

            print(f"Bot: {response.text}")

        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
