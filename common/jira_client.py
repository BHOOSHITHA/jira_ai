from jira import JIRA
from common.config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN

class JiraManager:
    def __init__(self):
        # connect to Jira
        self.jira = JIRA(server=JIRA_URL, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))

    def create_issue(self, project, summary, issue_type="Bug", priority="Medium", assignee=None):
        issue_dict = {
            'project': {'key': project},
            'summary': summary,
            'issuetype': {'name': issue_type},
            'priority': {'name': priority}
        }
        new_issue = self.jira.create_issue(fields=issue_dict)
        
        if assignee:
            # On Jira Cloud, we need accountID, but for simplicity in this student project,
            # we will assume the client passes a valid accountId or email if permissions allow.
            # (Free tier often requires Account ID, but the library handles name search sometimes)
            try:
                users = self.jira.search_users(query=assignee)
                if users:
                    self.jira.assign_issue(new_issue, users[0].accountId)
            except Exception as e:
                print(f"Warning: Could not assign user. {e}")
                
        return new_issue.key

    def transition_issue(self, issue_key, target_status):
        issue = self.jira.issue(issue_key)
        transitions = self.jira.transitions(issue)
        
        # Find the transition ID matching the name (e.g., "Done", "In Progress")
        t_id = None
        for t in transitions:
            if t['name'].lower() == target_status.lower():
                t_id = t['id']
                break
        
        if t_id:
            self.jira.transition_issue(issue, t_id)
            return True
        return False

    def add_comment(self, issue_key, comment_body):
        self.jira.add_comment(issue_key, comment_body)
        return True

    def get_issue_status(self, issue_key):
        issue = self.jira.issue(issue_key)
        return issue.fields.status.name