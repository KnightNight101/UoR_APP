import os
from git import Repo, GitCommandError
from datetime import datetime

class VCS:
    def __init__(self, project_path, db_logger=None):
        self.project_path = project_path
        self.repo_path = os.path.join(project_path, ".git")
        self.db_logger = db_logger
        self.repo = self._init_repo()

    def _init_repo(self):
        if not os.path.exists(self.repo_path):
            repo = Repo.init(self.project_path)
        else:
            repo = Repo(self.project_path)
        return repo

    def add_and_commit(self, file_path, author, message):
        rel_path = os.path.relpath(file_path, self.project_path)
        self.repo.index.add([rel_path])
        commit = self.repo.index.commit(message, author=author)
        commit_hash = commit.hexsha
        timestamp = datetime.fromtimestamp(commit.committed_date)
        if self.db_logger:
            self.db_logger.log_file_version(
                commit_hash=commit_hash,
                file=rel_path,
                author=author,
                timestamp=timestamp
            )
        return commit_hash

    def get_history(self, file_path):
        rel_path = os.path.relpath(file_path, self.project_path)
        commits = list(self.repo.iter_commits(paths=rel_path))
        history = []
        for commit in commits:
            history.append({
                "commit_hash": commit.hexsha,
                "author": commit.author.name,
                "timestamp": datetime.fromtimestamp(commit.committed_date),
                "message": commit.message.strip()
            })
        return history

    def get_diff(self, file_path, commit_hash1, commit_hash2):
        rel_path = os.path.relpath(file_path, self.project_path)
        diff = self.repo.git.diff(f"{commit_hash1}", f"{commit_hash2}", "--", rel_path)
        return diff

    def revert_file(self, file_path, commit_hash):
        rel_path = os.path.relpath(file_path, self.project_path)
        self.repo.git.checkout(commit_hash, "--", rel_path)
        # Optionally commit the revert
        return True

# Example DB logger stub
class DBLogger:
    def log_file_version(self, commit_hash, file, author, timestamp):
        # Implement DB logging here
        pass