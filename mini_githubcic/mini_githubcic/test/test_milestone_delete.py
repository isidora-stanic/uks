from django.test import TestCase, Client
from django.urls import reverse
from mini_githubcic.models import Milestone, Project, User
import datetime

class MilestoneDeleteTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.test_lead = User.objects.create(username='Utest', password='123')
        self.test_project = Project.objects.create(id=1, title='test project', description='desc', lead_id=1)

        self.logged_in_user = User.objects.create_user(username='U1', password='123')
        login = self.client.login(username='U1', password='123')

    def test_successful_delete_milestone(self):
        credentials = {'title': 'proba1', 'description': 'desc1', 'is_open': True,
                       'due_date': datetime.datetime.today()}
        response = self.client.post(reverse('add_milestone', args=[1]), credentials, follow=True)
        response = self.client.post(reverse('milestone_delete',args=[1]), {'id':1}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, len(response.context['milestones']))


    def test_delete_milestone_forbidden_acess(self):#todo
        credentials = {'title': 'proba1', 'description': 'desc1', 'is_open': True,
                       'due_date': datetime.datetime.today()}
        response = self.client.post(reverse('add_milestone', args=[1]), credentials, follow=True)
        response = self.client.post(reverse('milestone_delete', args=[1]), {'id': 1}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, len(response.context['milestones']))
