def fetch_url_readme(git_repo, branch='main'):
    if git_repo.endswith('.git'):
        git_repo = git_repo[:-4]

    if 'github.com' in git_repo:
        raw_url = git_repo.replace('github.com', 'raw.githubusercontent.com')
        url_readme = f"{raw_url}/{branch}/README.md"
    elif 'gitlab.com' in git_repo:
        raw_url = git_repo.replace('gitlab.com', 'gitlab.com')
        url_readme = f"{raw_url}/-/raw/{branch}/README.md"
    else:
        print("Unsupported Git repository platform.")
        return None

    print(f"Fetching {url_readme}...")
    return url_readme