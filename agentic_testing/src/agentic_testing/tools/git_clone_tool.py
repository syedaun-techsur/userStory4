import os
import shutil
from git import Repo, GitCommandError

DEFAULT_GITHUB_REPO = "https://github.com/dhruvraj-techsur/testing_automation.git"
DEFAULT_GITHUB_BRANCH = "full_stack_E2E_code"

def clone_repo(repo_url=DEFAULT_GITHUB_REPO, branch=DEFAULT_GITHUB_BRANCH, github_token=None):
    """
    Clone a GitHub repo/branch into a folder named after the repo in the project root.
    If the folder exists, it will be deleted first.
    If a GitHub token is provided (or set in the GITHUB_TOKEN env var), it will be used for authentication.
    """
    if github_token is None:
        github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        repo_url = repo_url.replace("https://", f"https://{github_token}@")

    # Always clone into the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
    repo_name = os.path.splitext(os.path.basename(repo_url.split('@')[-1].rstrip('/')))[0]
    target_path = os.path.join(project_root, repo_name)
    if os.path.exists(target_path):
        print(f"Deleting existing folder: {target_path}")
        shutil.rmtree(target_path)

    print(f"Cloning {repo_url} (branch: {branch}) into {target_path} ...")
    try:
        Repo.clone_from(repo_url, target_path, branch=branch, single_branch=True)
    except GitCommandError as e:
        print(f"Error during git clone: {e}")
        raise
    print(f"✅ Code fetched and saved to {target_path}") 