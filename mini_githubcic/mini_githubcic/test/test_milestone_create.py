#import unittest
from django.test import TestCase, Client
from django.urls import reverse
from mini_githubcic.models import Milestone, Project, User
import datetime
from mini_githubcic.views import MilestoneDetailView

class MilestoneCreateTest(TestCase):
    def setUp(self):
        self.client = Client()
        #self.all_ms = reverse('milestones/1')
        self.test_lead = User.objects.create(username='Utest', password='123')
        self.test_project = Project.objects.create(id=1, title='test project', description='desc', lead_id=1)

        self.logged_in_user = User.objects.create_user(username='U1', password='123')
        login = self.client.login(username='U1', password='123')

    def test_successful_create_milestone(self):

        credentials = {'title': 'proba1', 'description': 'desc1', 'is_open': True, 'due_date':datetime.datetime.today()+datetime.timedelta(days=3)}#

        response = self.client.post(reverse('add_milestone',args=[1]), credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(MilestoneDetailView is type(response.context['view']))
        #todo nekako da izvucem title

    def test_create_milestone_bad_input_date(self):
        credentials = {'title': 'proba1', 'description': 'desc1', 'is_open': True, 'due_date': 'neki string'}

        response = self.client.post(reverse('add_milestone', args=[1]), credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1,  len(response.context["form"].errors))
