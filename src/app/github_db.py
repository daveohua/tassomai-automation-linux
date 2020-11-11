import json
import os
from github import Github

class GithubDatabase:
    def __init__(self, path: str):
        self.path = path
        self.github = Github(os.environ.get('GITHUB_KEY'))
        self.repo = self.github.get_user().get_repo('tassomai-automation')

    def get_content(self):
        dataStr = self.repo.get_contents(self.path).decoded_content.decode('utf-8').strip()
        data = json.loads(dataStr)
        return data

    def edit_content(self, message, new_content):
        new_content = json.dumps(new_content, indent=3)
        if len(str(new_content)) < len(str(self.get_content())):
            return
        file = self.repo.get_contents(self.path)
        data = self.repo.update_file(self.path, message, new_content, file.sha)
        return data