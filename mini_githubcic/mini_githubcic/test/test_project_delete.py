from django.test import TestCase, Client
from django.urls import reverse
from mini_githubcic.models import Project, User


class ProjectDeleteTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.test_lead = User.objects.create(username='Utest', password='123')
        self.test_project = Project.objects.create(id=1, title='test project', description='desc', lead_id=1)

        self.logged_in_user = User.objects.create_user(username='U1', password='123')
        login = self.client.login(username='U1', password='123')

    def test_successful_delete_project(self):

        response = self.client.post(reverse('project_delete', args=[1]), {'id': 1}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, len(response.context['projects']))

