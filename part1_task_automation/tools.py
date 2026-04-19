import json
import requests
from requests.auth import HTTPBasicAuth
from common.config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN

# 1. Setup the Connection
auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# 2. The Universal Tool
def execute_jira_api(method: str, endpoint: str, data: str = None):
    """
    Executes a raw Jira REST API call.
    Args:
        method: HTTP method ("GET", "POST", "PUT", "DELETE").
        endpoint: The API path (e.g., "/rest/api/2/issue" or "/rest/api/2/search").
        data: (Optional) A JSON string containing the payload/body.
    """
    url = f"{JIRA_URL}{endpoint}"
    print(f"\n🔌 API CALL: {method} {url}")
    
    try:
        # Convert string JSON back to dict if provided
        json_data = json.loads(data) if data else None
        
        response = requests.request(
            method, 
            url, 
            headers=headers, 
            auth=auth, 
            json=json_data
        )
        
        # Handle empty responses (like Delete success)
        if response.status_code == 204:
            return "Success: 204 No Content"
            
        # Return the raw JSON from Jira so the AI can read it
        return response.text

    except Exception as e:
        return f"API Error: {str(e)}"

# Register this single tool
jira_tools = [execute_jira_api]