from django.test import TestCase
from mini_githubcic.models import *

import datetime

class MilestoneTestCase(TestCase):
    def setUp(self):
        project = Project.objects.create(id=1, title='test project', description='desc', lead_id=1)
        user = User.objects.create(username='U1', password='123')
        Notification.objects.create(user=user, is_reded=False, message="It is made new commit", project=project)

    def test_make_notification(self):
        project = Project.objects.get(id=1)
        user = User.objects.get(id=1)
        notification = Notification(user=user, is_reded=False, message="It is made new pull request", project=project)
        notification.save()
        notification1 = Notification.objects.get(id=2)
        self.assertEqual(notification.message, notification1.message)
        self.assertEqual(notification.project.id, notification1.project.id)

    # def test_edit_notification(self):
    #     notification = Notification.objects.get(id=1)
    #     milestone = Milestone.objects.get(id=1)
    #     notification.message = "it is made commit or pr"
    #     notification.save()
    #     self.assertEqual("it is made commit or pr", Notification.objects.get(id=1))

    def test_delete_notification(self):
        project = Project.objects.get(id=1)
        user = User.objects.get(id=1)
        notification = Notification(user=user, is_reded=False, message="deleting", project=project)
        notification.save()
        notification1 = Notification.objects.get(message="deleting")
        notification1.delete()
        try:
            Notification.objects.get(message="deleting")
            self.assertTrue(False)  # pronasao ga je a ne treba to da se desi with proveri sutra
        except:
            self.assertTrue(True) #jer ne postoji desi se greska i to je okej


    def test_get_notification(self):
        notification = Notification.objects.get(message="It is made new commit")

        self.assertEqual(notification.message, "It is made new commit")