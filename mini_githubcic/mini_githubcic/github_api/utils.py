import requests
from django.conf import settings
import base64


def get_access_token(request_token):
    """ Gets access token from Github API """
    response = requests.post(
        "https://github.com/login/oauth/access_token?client_id=" + settings.GITHUB_CLIENT_ID
        + "&client_secret=" + settings.GITHUB_CLIENT_SECRET
        + "&code=" + request_token,
        headers={'accept': 'application/json'}
    )
    return response


def get_github_auth_header(request):
    """
    Creating authorization header for HTTP request

    Format of the header is 'Authorization: Bearer <ACCESS_TOKEN>'
    Gets access token from session if user is authenticated on Github
    Otherwise it returns empty header

    Parameters
    ----------
    request : HttpRequest
        request with or without access token in its session

    Returns
    -------
    header : dict
        Authorization header
    """
    if 'access_token' in request.session:
        header = {
            'Authorization': 'Bearer ' + request.session['access_token'],
            'Content-Type': 'application/json'
        }
    else:
        header = {}
    return header


def send_github_req_with_auth(url, request):
    """
    Send GET request to Github API with access token
    Note: If there is no access token or if its expired or revoked, API will return 400 Bad credentials
    In this case use send_github_req_without_auth(url)
    """
    return requests.get(url, headers=get_github_auth_header(request))


def send_github_req_without_auth(url):
    """
    Send GET request to Github API without access token
    """
    return requests.get(url)


def send_github_req(url, request):
    """
    Send GET request to Github API without access token
    Returns response in json format
    """
    if 'access_token' in request.session:
        # if there is access token
        response = send_github_req_with_auth(url, request)
        if response.status_code == 401:
            # if access is revoked or expired
            # deletes invalid access token
            del request.session['access_token']
            request.session.modified = True
            response = send_github_req_without_auth(url)
            # to indicate that user needs to give access to github account
            # if he wants to make any changes and see his private repositories
            r = response.json()
            r['no_auth'] = True
            return r
    else:
        # if there is no access token
        response = send_github_req_without_auth(url)
    return response.json()


def decode_base64_file(enc):
    return base64.urlsafe_b64decode(enc).decode("utf-8")