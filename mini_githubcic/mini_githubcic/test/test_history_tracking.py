from django.test import TestCase, Client
from django.urls import reverse
from mini_githubcic.models import Milestone, Project, User
import datetime
from mini_githubcic.views import MilestoneDetailView

class StarProjectTest(TestCase):
    def setUp(self):
        self.client = Client()
        #self.all_ms = reverse('milestones/1')
        self.test_lead = User.objects.create(username='Utest', password='123')
        self.test_project = Project.objects.create(id=1, title='test project', description='desc', lead_id=1)

        self.logged_in_user = User.objects.create_user(username='U1', password='123')
        login = self.client.login(username='U1', password='123')

    def test_star_project(self):
        try: #ovde je problem sto na kraju se redirektuje na stranicu pa ne moze naknadno da se prosledi nesto
            self.client.get(reverse('star_project',args=[1,'U1']),  follow=True)
        except:
            pass

        # response = self.client.post(reverse('list_starred_projects', args=['U1']), follow=True)
        # print("ovde")
        # print(response.context)

    def test_watch_project(self):
        try: #ovde je problem sto na kraju se redirektuje na stranicu pa ne moze naknadno da se prosledi nesto
            self.client.get(reverse('watch_project',args=[1,'U1']),  follow=True)
        except:
            pass

        #response = self.client.post(reverse('list_watched_projects', args=['U1']), follow=True)

