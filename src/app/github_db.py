import json
from github import Github

class GithubDatabase:
    # If someone knows how to do this: Allowing the class to be used but not the code to be viewed, then dm me on discord - Gloryness#4341
    # Would really appreciate it!
    def __init__(self, path: str):
        self.path = path
        raise NotImplementedError("No usable implementation found!")

    def get_content(self):
        raise NotImplementedError("No usable implementation found!")

    def edit_content(self, message, new_content):
        raise NotImplementedError("No usable implementation found!")