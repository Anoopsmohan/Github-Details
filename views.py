"""Views for searching GitHub account, organization, and repository data."""
from collections import Counter
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
import json

from django.shortcuts import render


GITHUB_API = "https://api.github.com"


def index(request):
    """Render the index page."""
    return render(request, "index.html")


def _github_get(path):
    request = Request(
        f"{GITHUB_API}{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "github-details-django",
        },
    )
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def _username_from_post(request, field_name):
    return "-".join((request.POST.get(field_name) or "").strip().split())


def _error_message(value, exc):
    detail = getattr(exc, "reason", exc)
    return (
        f"The value you submitted ({value}) does not appear to be valid. "
        f"<br/>{detail}."
    )


def _user_and_repos(user_name):
    user = _github_get(f"/users/{quote(user_name)}")
    repos = _github_get(f"/users/{quote(user_name)}/repos?per_page=100&sort=updated")
    return user, repos


def _repo_year(repo):
    created_at = repo.get("created_at") or ""
    return created_at.split("-", 1)[0] if "-" in created_at else created_at


def username_search(request):
    if request.method != "POST":
        return render(request, "index.html")
    user_name = _username_from_post(request, "user_search")
    try:
        user, repos = _user_and_repos(user_name)
    except (HTTPError, URLError, TimeoutError) as exc:
        return render(
            request,
            "index.html",
            {"error": _error_message(request.POST.get("user_search"), exc)},
        )

    return render(
        request,
        "details.html",
        {
            "name": user_name,
            "lists": user,
            "repos": list(reversed(repos)),
            "org_type": {"type": user["login"] if user.get("type") == "Organization" else None},
            "message": "",
        },
    )


def topic_search(request):
    if request.method != "POST":
        return render(request, "index.html")
    topic = _username_from_post(request, "searchbox")
    try:
        result = _github_get(f"/search/repositories?q={quote(topic)}&per_page=100")
    except (HTTPError, URLError, TimeoutError) as exc:
        return render(
            request,
            "index.html",
            {"error": _error_message(request.POST.get("searchbox"), exc)},
        )

    repositories = [_normalize_search_repo(repo) for repo in result.get("items", [])]
    return render(
        request,
        "topic_details.html",
        {
            "data_list": repositories,
            "message": " " if repositories else "No data found. Please search another keyword.",
            "topic": topic,
            "num_result": result.get("total_count", len(repositories)),
        },
    )


def _normalize_search_repo(repo):
    owner = repo.get("owner") or {}
    login = owner.get("login", "")
    return {
        "name": repo.get("name"),
        "username": login,
        "description": repo.get("description"),
        "language": repo.get("language"),
        "owner": login,
        "created_at": repo.get("created_at"),
        "watchers": repo.get("watchers_count"),
        "homepage": repo.get("homepage"),
        "url": repo.get("html_url"),
    }


def details(request, user_name, topic_name=None):
    del topic_name
    user, repos = _user_and_repos(user_name)
    return render(
        request,
        "details.html",
        {
            "name": user_name,
            "lists": user,
            "repos": list(reversed(repos)),
            "org_type": {"type": user["login"] if user.get("type") == "Organization" else None},
        },
    )


def org_details(request, org_name, user_name=None):
    try:
        org_members = _github_get(f"/orgs/{quote(org_name)}/members?per_page=100")
        user = None
        repos = None
        if user_name:
            user, repos = _user_and_repos(user_name)
            repos = list(reversed(repos))
    except (HTTPError, URLError, TimeoutError):
        org_members = []
        user = None
        repos = None

    return render(
        request,
        "org_details.html",
        {
            "name_list": org_members,
            "org_name": org_name,
            "num_emp": len(org_members),
            "repos": repos,
            "lists": user,
        },
    )


def user_resume(request):
    if request.method != "POST":
        return render(request, "index.html")
    user_name = _username_from_post(request, "resume")
    try:
        user, repos = _user_and_repos(user_name)
    except (HTTPError, URLError, TimeoutError) as exc:
        return render(
            request,
            "index.html",
            {"error": _error_message(request.POST.get("resume"), exc)},
        )

    language_counts = Counter(
        repo.get("language")
        for repo in repos
        if repo.get("language") and not repo.get("fork")
    )
    total_languages = sum(language_counts.values())
    languages = {
        language: int((count / total_languages) * 100)
        for language, count in language_counts.items()
    } if total_languages else {}

    top_repositories = sorted(
        (
            {**repo, "created_at": _repo_year(repo), "priority": repo.get("watchers_count", 0) + repo.get("forks_count", 0)}
            for repo in repos
            if not repo.get("fork")
        ),
        key=lambda repo: repo["priority"],
        reverse=True,
    )[:5]

    created_at = (user.get("created_at") or "").split("-", 1)[0]
    return render(
        request,
        "resume.html",
        {
            "created_at": created_at,
            "lists": user,
            "repos": top_repositories,
            "orgs": None,
            "langs": languages,
            "message": "",
        },
    )
