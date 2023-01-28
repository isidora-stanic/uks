from django.test import SimpleTestCase
from django.urls import reverse, resolve
from mini_githubcic.views import *

class TestUrls(SimpleTestCase):

    def test_starr_url_is_resolved(self):
        url = reverse('star_project', args=[1, "U1"])
        self.assertEquals(resolve(url).func, starr_project)

    def test_watch_url_is_resolved(self):
        url = reverse('watch_project', args=[1, "U1"])
        self.assertEquals(resolve(url).func, watch_project)

    def test_unstarr_url_is_resolved(self):
        url = reverse('unstar_project', args=[1, "U1"])
        self.assertEquals(resolve(url).func, unstarr_project)

    def test_unwatch_url_is_resolved(self):
        url = reverse('unwatch_project', args=[1, "U1"])
        self.assertEquals(resolve(url).func, unwatch_project)

    def test_watched_projects_url_is_resolved(self):
        url = reverse('list_watched_projects', args=["U1"])
        self.assertEquals(resolve(url).func.__name__, "WatchedProjectListView")

    def test_starred_projects_url_is_resolved(self):
        url = reverse('list_starred_projects', args=["U1"])
        self.assertEquals(resolve(url).func.__name__, "StarredProjectListView")

    def test_notifications_url_is_resolved(self):
        url = reverse('list_notifications', args=["U1"])
        self.assertEquals(resolve(url).func.__name__, "MyNotificationsListView")