import os
import logging
import requests
import traceback

class GitHubIssueHandler(logging.Handler):
    def emit(self, record):
        try:
            log_message = self.format(record)

            title = f"[{record.levelname}] Action failed: {record.module}"
            body = (    
                f"## Log Report\n"
                f"- Log Level: {record.levelname}\n"
                f"- Module: {record.module}.py\n"
                f"- Functions: {record.funcName}()\n"
                f"- Line: {record.lineno}\n\n"
                f"## Log Message\n"
                f"- text: {log_message}\n"
            )

            create_github_issue(title, body)

        except Exception as e:
            print(f"GITHUB EXCEPTION | ERROR={e}")
            traceback.print_exc()

def create_github_issue(title: str, body: str) -> None:
    repo = os.getenv("GH_REPO")
    token = os.getenv("GH_TOKEN")

    if not repo or not token:
        print("GH_ISSUE_REPO_TOKEN_WARNING | WARNING=GH_REPO/GH_TOKEN not set; skipping GitHub issue creation.")
        return
    
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    payload = {"title": title, "body": body}

    r = requests.post(url, headers=headers, json=payload, timeout=10)
    if r.status_code >= 300:
        print(f"GH_ISSUE_CREATE_WARNING | WARNING=Failed to create issue: {r.status_code} {r.text[:200]}")