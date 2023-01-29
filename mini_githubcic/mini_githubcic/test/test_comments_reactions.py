from django.test import TestCase, Client
from django.urls import reverse
from mini_githubcic.models import Project, User, Issue, Comment, ReactionType, Reaction


class CommentsReactionsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_lead = User.objects.create(username='Utest', password='123')
        self.test_project = Project.objects.create(id=1, title='test project', description='desc', lead_id=1)
        self.test_issue = Issue.objects.create(id=1, title="test issue", description="i1", creator_id=1, project_id=1,
                                               is_open=True)
        self.test_comment = Comment.objects.create(id=1, content="test", author_id=1, task_id=1)
        self.test_reaction = Reaction.objects.create(id=1, type=ReactionType.LIKE, comment_id=1, user_id=1)
        self.logged_in_user = User.objects.create_user(username='U1', password='123')
        self.client.login(username='U1', password='123')

    def test_successful_add_reaction(self):
        response = self.client.get(reverse('comment_reaction', args=[1, 'LIKE']), {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['comments'][0].get('reactions')) is 2)
        self.assertTrue(response.context['comments'][0].get('reactions')[1].type == ReactionType.LIKE)

    # def test_successful_remove_reaction(self):
    #     response = self.client.get(reverse('comment_reaction', args=[1, 'LIKE']), {}, follow=True)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue(len(response.context['comments'][0].get('reactions')) is 1)
