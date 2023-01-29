from django.test import SimpleTestCase
from django.urls import reverse, resolve
from mini_githubcic.views import *


class TestProjectUrls(SimpleTestCase):

    def test_get_all_url_is_resolved(self):
        url = reverse('list_projects')
        self.assertEquals(resolve(url).func, 'ProjectListView')

    def test_add_project_url_is_resolved(self):
        url = reverse('add_project')
        self.assertEquals(resolve(url).func, 'ProjectCreateView')

    def test_detail_url_is_resolved(self):
        url = reverse('project_detail', args=[1])
        self.assertEquals(resolve(url).func.__name__, 'ProjectDetailView')

    def test_delete_url_is_resolved(self):
        url = reverse('project_delete', args=[1])
        self.assertEquals(resolve(url).func.__name__, 'ProjectUpdateView')

    def test_update_url_is_resolved(self):
        url = reverse('project_update', args=[1, 'LIKE'])
        self.assertEquals(resolve(url).func.__name__, 'ProjectDeleteView')
