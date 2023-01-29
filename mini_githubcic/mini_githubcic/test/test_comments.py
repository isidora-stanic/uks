from django.test import TestCase
from mini_githubcic.models import *


class CommentsTestCase(TestCase):
    def setUp(self):
        p1 = Project.objects.create(id=1, title='test project', description='desc', lead_id=1)
        u1 = User.objects.create(username='U1', password='123')
        i1 = Issue.objects.create(title="issue1", description="i1", creator=u1, assigned_to=u1, project=p1, is_open=True)
        Comment.objects.create(content="test", author=u1, task=i1)

    def test_create_comment(self):
        user = User.objects.get(id=1)
        issue = Issue.objects.get(id=1)
        comment = Comment(content="test1", author=user, task=issue)
        comment.save()
        comment1 = Comment.objects.filter(content="test1").first()
        self.assertEqual(comment.content, comment1.content)
        self.assertEqual(comment1.task, comment1.task)
        self.assertEqual(comment1.author, comment1.author)

    def test_delete_comment(self):
        user = User.objects.get(id=1)
        issue = Issue.objects.get(id=1)
        comment = Comment(content="delete", author=user, task=issue)
        comment.save()
        comment1 = Comment.objects.get(content="delete")
        comment1.delete()
        try:
            Comment.objects.get(content="delete")
            self.assertTrue(False)
        except:
            self.assertTrue(True)

    def test_get_comment(self):
        comment = Comment.objects.get(content="test")
        self.assertEqual(comment.content, "test")
