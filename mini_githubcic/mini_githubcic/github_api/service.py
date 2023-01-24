"""
var axios = require('axios');
var fs = require('fs');
var base64 = require('base-64');

let token = "ghp_SgpPBp7XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
let file = fs.readFileSync("abc.txt").toString();
console.log(file);
var content = base64.encode(file);
console.log(content);
uploadFileApi(token, content)

function uploadFileApi(token, content) {

    var data = JSON.stringify({
        "message": "txt file",
        "content": `${content}`
    });

    var config = {
        method: 'put',
        url: 'https://api.github.com/repos/sumit-s03/Test/contents/abc.txt',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        data: data
    };

    axios(config)
        .then(function (response) {
            console.log(JSON.stringify(response.data));
        })
        .catch(function (error) {
            console.log(error);
        });
}
"""
from mini_githubcic.github_api.utils import send_github_req


def search_repositories_by_user(request, username):
    return send_github_req(
        'https://api.github.com/search/repositories?q=user:'+username,
        request
    )


def get_all_visible_repositories_by_user(request, username):
    return send_github_req('https://api.github.com/users/'+username+'/repos', request)


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


def compare_two_branches(request, username, repo, base, head):
    return send_github_req('https://api.github.com/repos/' + username + '/' + repo + '/compare/' + base + '...' + head, request)


def create_file_url(github_file_url):
    print(github_file_url)
    return github_file_url


def create_folder_url(github_folder_url):
    print(github_folder_url)
    return github_folder_url

def get_commit_changes(request, username, repo, sha):#"59e3d110bf4bfd5ec22c18193421942a6a56e2ac"
    return send_github_req('https://api.github.com/repos/' + username + '/' + repo + '/commits/' + sha, request)