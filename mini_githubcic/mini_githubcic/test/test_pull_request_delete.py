from django.test import TestCase, Client
from django.urls import reverse
from mini_githubcic.models import Project, User, Branch, PullRequest


class PullRequestDeleteTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.test_lead = User.objects.create(username='Utest', password='123')
        self.test_project = Project.objects.create(id=1, title='test project', description='desc', lead_id=1)
        self.source = Branch.objects.create(id=1, name='b1', project_id=1)
        self.target = Branch.objects.create(id=2, name='b2', project_id=1)
        self.pull_request = PullRequest\
            .objects\
            .create(
                id=1,
                title='pr1',
                project=self.test_project,
                creator=self.test_lead,
                source=self.source,
                target=self.target
        )

        self.logged_in_user = User.objects.create_user(username='U1', password='123')
        login = self.client.login(username='U1', password='123')

    def test_successful_delete_pull_request(self):

        response = self.client.post(reverse('pull_request_delete', args=[1]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, len(response.context['pull_requests']))

