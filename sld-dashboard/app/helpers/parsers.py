import urllib.parse


def fetch_url_readme(git_repo, branch='main'):
    if not git_repo.endswith('.git'):
        git_repo += '.git'

    parsed_url = urllib.parse.urlparse(git_repo)
    
    if parsed_url.netloc == 'github.com':
        raw_url = f"https://raw.githubusercontent.com/{parsed_url.path[1:-4]}"
        url_readme = f"{raw_url}/{branch}/README.md"
    elif parsed_url.netloc == 'gitlab.com':
        raw_url = f"https://gitlab.com/{parsed_url.path[1:-4]}"
        url_readme = f"{raw_url}/-/raw/{branch}/README.md"
    else:
        print("Unsupported Git repository platform.")
        return None

    print(f"Fetching {url_readme}...")
    return url_readme
