from django.test import TestCase, Client
from django.urls import reverse
from mini_githubcic.models import Project, User, Branch, Label
from mini_githubcic.views import ProjectDetailView


class ProjectCreateTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_developer = User.objects.create(username='Utest', password='123')
        self.test_project = Project.objects.create(id=1, title='test project', description='desc', lead_id=1)
        self.source = Branch.objects.create(id=1, name='b1', project_id=1)
        self.target = Branch.objects.create(id=2, name='b2', project_id=1)

        self.label = Label.objects.create(id=1, name='l1', project=self.test_project)
        self.logged_in_user = User.objects.create_user(username='U1', password='123')
        login = self.client.login(username='U1', password='123')

    def test_successful_create_pull_request(self):

        credentials = {
            'title': 'pr',
            'description': 'd',
            'assigned_to': self.test_developer,
            'source': self.source,
            'target': self.target,
            'labels': [self.label]
        }

        response = self.client.post(reverse('add_pull_request', args=[1]), credentials, follow=True)
        self.assertEqual(response.status_code, 200)