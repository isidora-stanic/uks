from django.test import TestCase, Client
from django.urls import reverse
from mini_githubcic.models import Milestone, Project, User
from datetime import datetime
from mini_githubcic.views import MilestoneDetailView

class MilestoneEditTest(TestCase):
    def setUp(self):
        self.client = Client()
        # self.all_ms = reverse('milestones/1')
        self.test_lead = User.objects.create(username='Utest', password='123')
        self.test_project = Project.objects.create(id=1, title='test project', description='desc', lead_id=1)
        self.milestone = Milestone.objects.create(title='proba1', description='desc1', is_open=True,
                                                  due_date=datetime.today(), project_id=1)

        self.logged_in_user = User.objects.create_user(username='U1', password='123')
        login = self.client.login(username='U1', password='123')

    def test_successful_edit_milestone(self):
        # credentials = {'title': 'proba1', 'description': 'desc1', 'is_open': True,
        #                'due_date': datetime.today()}  #
        credentials2 = {'title': 'proba2', 'description': 'descc33', 'is_open': True,
                       'due_date': datetime.today()}

        # response = self.client.post(reverse('add_milestone', args=[1]), credentials, follow=True)
        response2 = self.client.post(reverse('milestone_update', args=[1]), credentials2, follow=True)
        self.assertEqual(response2.status_code, 200)
        self.assertTrue(MilestoneDetailView is type(response2.context['view']))
        # todo nekako da izvucem title

    def test_edit_milestone_bad_input_date(self):
        # credentials = {'title': 'proba1', 'description': 'desc1', 'is_open': True,
        #                'due_date': datetime.today()}
        credentials2 = {'title': 'proba2', 'description': 'descc33', 'is_open': True,
                        'due_date': "--------------"}

        # response = self.client.post(reverse('add_milestone', args=[1]), credentials, follow=True)
        response2 = self.client.post(reverse('milestone_update', args=[1]), credentials2, follow=True)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(1, len(response2.context["form"].errors))