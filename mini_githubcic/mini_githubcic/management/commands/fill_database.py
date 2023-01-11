from django.core.management.base import BaseCommand

from mini_githubcic.models import *
import uuid


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
        p1.save()
        p1.developers.add(u1)
        p1.save()

        p2 = Project(title="test", description="d2", licence="l2", visibility=Visibility.PUBLIC,
                     link="https://github.com/" + u2.username + "/test.git", lead=u2)
        p2.save()
        p2.developers.add(u1)
        p2.developers.add(u2)
        p2.save()

        p3 = Project(title="gitic", description="d3", licence="l3", visibility=Visibility.PRIVATE,
                     link="https://github.com/" + u3.username + "/gitic.git", lead=u3)
        p3.save()
        p3.developers.add(u3)
        p3.save()

    def _insert_issues(self):
        Issue.objects.all().delete()

        u1 = User.objects.get(username="U1")
        u2 = User.objects.get(username="U2")
        u3 = User.objects.get(username="U3")

        p1 = Project.objects.get(description="d1")
        p2 = Project.objects.get(description="d2")
        p3 = Project.objects.get(description="d3")

        i1 = Issue(title="issue1", description="i1", creator=u1, assigned_to=u1, project=p1, is_open=True)
        i1.save()

        i2 = Issue(title="issue2", description="i2", creator=u2, assigned_to=u2, project=p2, is_open=True)
        i2.save()

        i3 = Issue(title="issue3", description="i3", creator=u1, assigned_to=u3, project=p3, is_open=True)
        i3.save()

        i4 = Issue(title="issue4", description="i4", creator=u1, assigned_to=u1, project=p1, is_open=False)
        i4.save()

    def _insert_milestones(self):
        Milestone.objects.all().delete()

        p2 = Project.objects.get(description="d2")

        m1 = Milestone(title="milestone1", description="i1", project=p2, is_open=True)
        m1.save()

    def _insert_labels(self):
        Label.objects.all().delete()

        p1 = Project.objects.get(description="d1")
        l1 = Label(name="l1", description="d2", color="#FFFFFF", project=p1)
        l1.save()

    def _insert_commits_and_branches(self):
        Branch.objects.all().delete()
        Commit.objects.all().delete()

        p1 = Project.objects.get(description="d1")
        u1 = User.objects.get(username="U1")

        b1 = Branch(name="main", project=p1)
        b1.save()

        b2 = Branch(name="develop", project=p1)
        b2.save()

        c1 = Commit(branch=b1, author=u1, hash=str(uuid.uuid4().hex), log_message="root commit (no parent)")
        c1.save()

        c2 = Commit(branch=b1, author=u1, hash=str(uuid.uuid4().hex), log_message="first after root (root is a parent)")
        c2.save()
        c2.parents.add(c1)
        c2.save()
        print(c2.parents.all())

        c3 = Commit(branch=b2, author=u1, hash=str(uuid.uuid4().hex), log_message="first on new branch after root (root is a parent)")
        c3.save()
        c3.parents.add(c1)
        c3.save()
        print(c3.parents.all())

        c4 = Commit(branch=b1, author=u1, hash=str(uuid.uuid4().hex),
                    log_message="merging two branches (2 parent commits)")
        c4.save()
        c4.parents.add(c2, c3)
        c4.save()
        print(c4.parents.all())

    def handle(self, *args, **options):
        self._insert_users()
        self._insert_projects()
        self._insert_issues()
        self._insert_milestones()
        self._insert_labels()
        self._insert_commits_and_branches()
