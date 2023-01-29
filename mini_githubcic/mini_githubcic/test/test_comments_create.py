from django.test import TestCase, Client
from django.urls import reverse
from mini_githubcic.models import Project, User, Issue, PullRequest, Branch, State
from mini_githubcic.forms import CommentForm


class CommentsCreateTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_lead = User.objects.create(username='Utest', password='123')
        self.test_project = Project.objects.create(id=1, title='test project', description='desc', lead_id=1)
        self.test_issue = Issue.objects.create(id=1, title="test issue", description="i1", creator_id=1, project_id=1,
                                               is_open=True)
        self.target_branch = Branch.objects.create(id=1, name='target', project_id=1)
        self.source_branch = Branch.objects.create(id=2, name='source', project_id=1)
        self.test_pr = PullRequest.objects.create(id=2, title="test pr", description="i1", creator_id=1, project_id=1,
                                                  state=State.OPEN, target_id=1, source_id=2)

        self.logged_in_user = User.objects.create_user(username='U1', password='123')
        login = self.client.login(username='U1', password='123')

    def test_successful_create_comment_in_issue(self):
        credentials = {'content': 'proba'}
        response = self.client.post(reverse('issue_detail', args=[1]), credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CommentForm is type(response.context['comment_form']))

    def test_successful_create_comment_in_pull_request(self):
        credentials = {'content': 'proba'}
        response = self.client.post(reverse('pull_request_detail', args=[2]), credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CommentForm is type(response.context['comment_form']))
