from django.test import TestCase
from mini_githubcic.models import *

import datetime

class MilestoneTestCase(TestCase):
    def setUp(self):
        project = Project.objects.create(id=1, title='test project', description='desc', lead_id=1)
        User.objects.create(username='U1', password='123')
        Milestone.objects.create(title="test", description="d1", due_date=datetime.datetime.now(timezone.utc), project=project, is_open=True)

    def test_make_milestone(self):
        project = Project.objects.get(id=1)
        milestone = Milestone(title="t1",description = "d1", due_date=datetime.datetime.now(timezone.utc),project=project,is_open=True)
        milestone.save()
        milestone1 = Milestone.objects.get(title="t1")
        self.assertEqual(milestone.title, milestone1.title)
        self.assertEqual(milestone.description, milestone1.description)

    def test_delete_milestone(self):
        project = Project.objects.get(id=1)
        milestone = Milestone(title="deleting",description = "d1", due_date=datetime.datetime.now(timezone.utc),project=project,is_open=True)
        milestone.save()
        milestone1 = Milestone.objects.get(title="deleting")
        milestone1.delete()
        try:
            Milestone.objects.get(title="deleting")
            self.assertTrue(False)  # pronasao ga je a ne treba to da se desi with proveri sutra
        except:
            self.assertTrue(True) #jer ne postoji desi se greska i to je okej


    def test_get_milestone(self):
        milestone = Milestone.objects.get(title="test")

        self.assertEqual(milestone.title, "test")