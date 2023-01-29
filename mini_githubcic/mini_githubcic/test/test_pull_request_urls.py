from django.test import SimpleTestCase
from django.urls import reverse, resolve
from mini_githubcic.views import *


class TestPullRequestUrls(SimpleTestCase):

    def test_get_all_url_is_resolved(self):
        url = reverse('list_pull_requests', args=[1])
        self.assertEquals(resolve(url).url_name, 'list_pull_requests')

    def test_add_pull_request_url_is_resolved(self):
        url = reverse('add_pull_request', args=[1])
        self.assertEquals(resolve(url).url_name, 'add_pull_request')

    def test_delete_url_is_resolved(self):
        url = reverse('pull_request_delete', args=[1])
        self.assertEquals(resolve(url).url_name, 'pull_request_delete')

    def test_update_url_is_resolved(self):
        url = reverse('pull_request_update', args=[1])
        self.assertEquals(resolve(url).url_name, 'pull_request_update')