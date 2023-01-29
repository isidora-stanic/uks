from django.test import TestCase, Client
from django.urls import reverse
from mini_githubcic.models import Project, User, Comment, Issue


class CommentDeleteTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.test_lead = User.objects.create(username='Utest', password='123')
        self.test_project = Project.objects.create(id=1, title='test project', description='desc', lead_id=1)
        self.test_issue = Issue.objects.create(id=1, title="test issue", description="i1", creator_id=1, project_id=1,
                                               is_open=True)
        self.test_comment = Comment.objects.create(id=1, content="test", author_id=1, task_id=1)
        self.logged_in_user = User.objects.create_user(username='U1', password='123')
        login = self.client.login(username='U1', password='123')

    def test_successful_delete_comment(self):
        response = self.client.post(reverse('comment_delete',args=[1]), {'id':1}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, len(response.context['comments']))

