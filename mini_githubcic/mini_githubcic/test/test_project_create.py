from django.test import TestCase, Client
from django.urls import reverse
from mini_githubcic.models import Project, User, Visibility
from mini_githubcic.views import ProjectDetailView


class ProjectCreateTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_developer = User.objects.create(username='Utest', password='123')

        self.logged_in_user = User.objects.create_user(username='U1', password='123')
        login = self.client.login(username='U1', password='123')

    def test_successful_create_project(self):

        credentials = {
            'title': 'title',
            'description': 'description',
            'licence': 'licence',
            'visibility': Visibility.PUBLIC
        }

        response = self.client.post(reverse('add_project'), credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProjectDetailView, type(response.context['view']))
