from django.core.management.base import BaseCommand

from ..models import User, Project, Visibility


class Command(BaseCommand):

    def _insert_users(self):
        User.objects.all().delete()

        u1 = User(username="U1", password="123")
        u1.save()

        u2 = User(username="U2", password="123")
        u2.save()

        u3 = User(username="U3", password="123")
        u3.save()

    def _insert_projects(self):
        Project.objects.all().delete()

        u1 = User.objects.get(username="U1")
        u2 = User.objects.get(username="U2")
        u3 = User.objects.get(username="U3")

        p1 = Project(title="project", description="d1", licence="l1", visibility=Visibility.PUBLIC,
                     link="https://github.com/" + u1.username + "/project.git", lead=u1)
        p1.developers.add(u1)
        p1.save()

        p2 = Project(title="test", description="d2", licence="l2", visibility=Visibility.PUBLIC,
                     link="https://github.com/" + u2.username + "/test.git", lead=u2)
        p2.developers.add(u1)
        p2.developers.add(u2)
        p2.save()

        p3 = Project(title="gitic", description="d3", licence="l3", visibility=Visibility.PRIVATE,
                     link="https://github.com/" + u3.username + "/gitic.git", lead=u3)
        p3.developers.add(u3)
        p3.save()

    def handle(self, *args, **options):
        self._insert_users()
        self._insert_projects()
