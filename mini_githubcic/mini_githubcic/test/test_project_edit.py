from django.test import TestCase, Client
from django.urls import reverse
from mini_githubcic.models import Project, User, Visibility
from datetime import datetime
from mini_githubcic.views import ProjectUpdateView


class ProjectEditTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_lead = User.objects.create(username='Utest', password='123')
        self.test_project = Project.objects.create(id=1, title='test project', description='desc', lead_id=1)

        self.logged_in_user = User.objects.create_user(username='U1', password='123')
        login = self.client.login(username='U1', password='123')

    def test_successful_edit_project(self):
        test_developer = User.objects.create(username='Dev', password='123')
        credentials2 = {
            'title': 'updated',
            'description': 'desc',
            'developers': [test_developer],
            'visibility': Visibility.PRIVATE,
            'licence': 'licence'
        }

        response = self.client.post(reverse('project_update', args=[1]), credentials2, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['project'].title, 'updated')
        self.assertEqual(ProjectUpdateView, type(response.context['view']))
