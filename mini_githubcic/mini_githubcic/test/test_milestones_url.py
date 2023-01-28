from django.test import SimpleTestCase
from django.urls import reverse, resolve
from mini_githubcic.views import *

class TestMilestoneUrls(SimpleTestCase):

    def test_get_all_url_is_resolved(self):
        url = reverse('list_milestones', args=[1])
        self.assertEquals(resolve(url).func.__name__, "MilestoneListView")

    def test_add_milestone_url_is_resolved(self):
        url = reverse('add_milestone', args=[1])
        self.assertEquals(resolve(url).func.__name__, 'MilestoneCreateView')

    def test_detail_url_is_resolved(self):
        url = reverse('milestone_detail', args=[1])
        self.assertEquals(resolve(url).func.__name__, 'MilestoneDetailView')

    def test_delete_url_is_resolved(self):
        url = reverse('milestone_delete', args=[1])
        self.assertEquals(resolve(url).func.__name__, 'MilestoneDeleteView')

    def test_update_url_is_resolved(self):
        url = reverse('milestone_update', args=[1])
        self.assertEquals(resolve(url).func.__name__, 'MilestoneUpdateView')

    def test_close_url_is_resolved(self):
        url = reverse('milestone_close', args=[1])
        self.assertEquals(resolve(url).func, milestone_close)