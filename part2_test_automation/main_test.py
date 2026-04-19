# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from part2_test_automation.test_generator import TestRuleParser
# from part2_test_automation.test_runner import TestEngine

# def main():
#     print("🟩 JIRA TEST AUTOMATION STARTED")
#     print("Enter a business rule to test (e.g., 'A bug cannot be closed if priority is high')")
    
#     parser = TestRuleParser()
#     engine = TestEngine()

#     while True:
#         rule = input("\nEnter Rule (or 'exit'): ")
#         if rule == "exit": break

#         # 1. Parse Rule
#         test_case = parser.parse_rule(rule)
#         print(f"DEBUG: Generated Test Case: {test_case}")

#         # 2. Run Test
#         status = engine.run_test(test_case)
#         print(f"🏁 Final Test Status: {status}")

# if __name__ == "__main__":
#     main()

import sys
import os
import requests
from requests.auth import HTTPBasicAuth

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- NEW SDK IMPORTS ---
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Reuse tools from Part 1
from part1_task_automation.tools import jira_tools 

current_dir = os.path.dirname(os.path.abspath(__file__))

load_dotenv(
    dotenv_path=os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", ".env")
    ),
    override=True
)

def get_my_account_id():
    url = f"{os.getenv('JIRA_URL')}/rest/api/3/myself"
    auth = HTTPBasicAuth(os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN'))
    try:
        r = requests.get(url, headers={"Accept": "application/json"}, auth=auth)
        return r.json().get('accountId')
    except:
        return "unknown"

my_id = get_my_account_id()

SYSTEM_PROMPT = f"""
You are an Autonomous QA Engineer for Jira. 
Your goal is to VALIDATE business rules by executing live tests on the Jira Cloud API.

USER INPUT: A business rule (e.g., "A bug cannot be closed if priority is high").

YOUR TESTING PROTOCOL:
1. **Analyze**: Understand the condition and restriction.
2. **Setup**: Create a *temporary* test issue.
3. **Execute**: Attempt the restricted action.
4. **Assert**: 
   - If rule says "Cannot" and API fails (Error 400/403) -> **PASS**.
   - If rule says "Cannot" and API succeeds (200 OK) -> **FAIL**.
5. **Cleanup**: ALWAYS delete the test issue.


OUTPUT: Print "🧪 TEST RESULT: [PASS/FAIL]" and the reason.

CONTEXT:
- Project Key: '{os.getenv("JIRA_PROJECT_KEY")}'
- Current User ID: '{my_id}'
"""


def main():
    print("🟩 JIRA TEST AGENT (Powered by google-genai v1.0)")
    
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=jira_tools,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
        )
    )

    while True:
        rule = input("\nEnter Rule to Test (or 'exit'): ")
        if rule.lower() in ["exit", "quit"]: break

        print(f"\n🤖 Designing test plan for: '{rule}'...\n")
        
        try:
            response = chat.send_message(rule)
            print(f"{response.text}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()