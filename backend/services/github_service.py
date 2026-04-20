"""GitHub API wrapper — repo health, commits, PRs via PyGitHub."""

from datetime import datetime, timezone
from typing import Optional

from backend.config import settings

_github = None


def _get_github():
    """Get authenticated GitHub instance (singleton)."""
    global _github
    if _github is None:
        token = settings.GITHUB_TOKEN
        if not token or token.startswith("ghp_REPLACE"):
            return None
        from github import Github

        _github = Github(token)
    return _github


def is_github_configured() -> bool:
    """Check if GitHub token is available."""
    token = settings.GITHUB_TOKEN
    return bool(token) and not token.startswith("ghp_REPLACE")


def get_repo_info(repo_name: str) -> Optional[dict]:
    """Get detailed info for a GitHub repo."""
    gh = _get_github()
    if not gh:
        return None

    try:
        full_name = "{}/{}".format(settings.GITHUB_ORG, repo_name)
        repo = gh.get_repo(full_name)

        # Last commit
        last_commit = None
        commit_age = None
        c = next(iter(repo.get_commits()), None)
        if c:
            last_commit = c.commit.message.split("\n")[0][:80]
            commit_date = c.commit.committer.date.replace(tzinfo=timezone.utc)
            age_days = (datetime.now(timezone.utc) - commit_date).days
            if age_days == 0:
                commit_age = "today"
            elif age_days == 1:
                commit_age = "yesterday"
            elif age_days < 7:
                commit_age = "{} days ago".format(age_days)
            elif age_days < 30:
                commit_age = "{} weeks ago".format(age_days // 7)
            else:
                commit_age = "{} months ago".format(age_days // 30)

        # Open PRs and issues
        open_prs = repo.get_pulls(state="open").totalCount
        open_issues = repo.get_issues(state="open").totalCount - open_prs  # issues includes PRs

        # Health rating
        health = "good"
        if commit_age and ("month" in commit_age):
            health = "caution"
        elif commit_age and ("week" in commit_age):
            health = "fair"
        if open_prs > 5:
            health = "caution" if health == "good" else health

        return {
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "default_branch": repo.default_branch,
            "health": health,
            "last_commit": last_commit,
            "commit_age": commit_age,
            "open_prs": open_prs,
            "open_issues": max(0, open_issues),
            "stars": repo.stargazers_count,
            "size_kb": repo.size,
            "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
        }
    except Exception as e:
        return {"name": repo_name, "error": str(e), "health": "error"}


def list_org_repos() -> list:
    """List all repos in the GitHub org."""
    gh = _get_github()
    if not gh:
        return []

    try:
        org = gh.get_organization(settings.GITHUB_ORG)
        repos = []
        for repo in org.get_repos(sort="updated", direction="desc"):
            repos.append(
                {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "default_branch": repo.default_branch,
                    "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
                    "size_kb": repo.size,
                }
            )
        return repos
    except Exception:
        return []
