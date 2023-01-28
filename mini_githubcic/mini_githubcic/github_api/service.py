from mini_githubcic.github_api.utils import send_github_req, send_github_req_with_auth


def get_user_info(request):
    user_info_resp = send_github_req_with_auth('https://api.github.com/user', request)
    if(user_info_resp.status_code == 401):
        request.user.access_token = ""
        request.user.save()
    return user_info_resp

def search_repositories_by_user(request, username):
    return send_github_req(
        'https://api.github.com/search/repositories?q=user:'+username,
        request
    )


def get_all_visible_repositories_by_user(request):
    return send_github_req_with_auth('https://api.github.com/user/repos', request)


def get_specific_repository(request, username, repo):
    return send_github_req('https://api.github.com/repos/'+username+'/'+repo, request)


def get_specific_repository_readme(request, username, repo):
    return send_github_req('https://api.github.com/repos/'+username+'/'+repo+'/readme', request)


def get_repository_tree(request, username, repo, branch='master'):
    branch_info = get_repository_branch(request, username, repo, branch)
    # master = master.json()
    head_tree_sha = branch_info['commit']['commit']['tree']['sha']
    # head_tree_sha = '123'
    print("supposedly tree sha", branch_info['commit']['commit']['tree']['sha'])
    return send_github_req('https://api.github.com/repos/'+username+'/'+repo+'/git/trees/'+head_tree_sha, request)


def get_repository_branch(request, username, repo, branch):
    return send_github_req('https://api.github.com/repos/'+username+'/'+repo+'/branches/'+branch, request)


def get_subtree(request, username, repo, subtree_sha):
    return send_github_req('https://api.github.com/repos/'+username+'/'+repo+'/git/trees/'+subtree_sha, request)


def get_file_content(request, username, repo, path):
    return send_github_req('https://api.github.com/repos/'+username+'/'+repo+'/contents/'+path, request)


def get_tree_recursively(request, username, repo, branch='master'):
    branch_info = get_repository_branch(request, username, repo, branch)
    # master = master.json()
    head_tree_sha = branch_info['commit']['commit']['tree']['sha']
    return send_github_req('https://api.github.com/repos/'+username+'/'+repo+'/git/trees/'+head_tree_sha+'?recursive=1', request)


def get_all_branches(request, username, repo):
    return send_github_req('https://api.github.com/repos/'+username+'/'+repo+'/branches', request)


def get_all_commits_for_branch(request, username, repo, branch):
    return send_github_req('https://api.github.com/repos/'+username+'/'+repo+'/commits?sha='+branch, request)


def create_branch(request, username, repo, branch, commit_sha):
    return send_github_req('https://api.github.com/repos/'+username+'/'+repo+'/git/refs', request,
                           method='POST', data='{"ref": "refs/heads/'+branch+'", "sha": "'+commit_sha+'"}')


def rename_branch(request, username, repo, branch, new_name):
    return send_github_req('https://api.github.com/repos/'+username+'/'+repo+'/branches/'+branch+'/rename', request,
                           method="POST", data='{"new_name": "'+new_name+'"}')


def delete_branch(request, username, repo, branch):
    print('AYOOOOOOOOOO','https://api.github.com/repos/'+username+'/'+repo+'/git/refs/heads/'+branch)
    r = send_github_req('https://api.github.com/repos/'+username+'/'+repo+'/git/refs/heads/'+branch, request,
                           method='DELETE')
    print(r)
    return r


def compare_two_branches(request, username, repo, base, head):
    return send_github_req('https://api.github.com/repos/'+username+'/'+repo+'/compare/'+base+'...'+head, request)


def merge_branches(request, username, repo, base, head, msg):
    return send_github_req('https://api.github.com/repos/' + username + '/' + repo + '/merges', request,
                    metod='POST', data='{"base":"'+base+'", "head": "'+head+'", "commit_message": "'+msg+'"}')


def merge_usptream_branch(request, username, repo, upstream_branch):
    """
    Sync a fork branch with the upstream repository
    Sync a branch of a forked repository to keep it up-to-date with the upstream repository.
    """
    return send_github_req('https://api.github.com/repos/' + username + '/' + repo + '/merge-upstream', request,
                           method='POST', data='{"branch":"'+upstream_branch+'"}')


def create_file_url(github_file_url):
    print(github_file_url)
    return github_file_url


def create_folder_url(github_folder_url):
    print(github_folder_url)
    return github_folder_url

def get_commit_changes(request, username, repo, sha):#"59e3d110bf4bfd5ec22c18193421942a6a56e2ac"
    return send_github_req('https://api.github.com/repos/' + username + '/' + repo + '/commits/' + sha, request)

def git_fork_projects(request, username, repo):
    return send_github_req('https://api.github.com/repos/' + username + '/' + repo + '/forks', request, method='POST')