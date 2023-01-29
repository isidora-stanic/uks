from django.test import SimpleTestCase
from django.urls import reverse, resolve
from mini_githubcic.views import *


class TestCommentUrls(SimpleTestCase):

    def test_add_comment_to_issue_url_is_resolved(self):
        url = reverse('issue_detail', args=[1])
        self.assertEquals(resolve(url).func, new_comment)

    def test_add_comment_to_pull_request_url_is_resolved(self):
        url = reverse('pull_request_detail', args=[1])
        self.assertEquals(resolve(url).func, pull_request_new_comment)

    def test_delete_url_is_resolved(self):
        url = reverse('comment_delete', args=[1])
        self.assertEquals(resolve(url).func.__name__, 'CommentDeleteView')

    def test_update_url_is_resolved(self):
        url = reverse('comment_update', args=[1])
        self.assertEquals(resolve(url).func.__name__, 'CommentUpdateView')

    def test_reaction_url_is_resolved(self):
        url = reverse('comment_reaction', args=[1, 'LIKE'])
        self.assertEquals(resolve(url).func, toggle_reaction)
