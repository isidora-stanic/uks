from django.db import models
from django.utils import timezone
from django.urls import reverse


class State(models.TextChoices):
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
    MERGED = 'MERGED'


class Visibility(models.TextChoices):
    PUBLIC = 'PUBLIC'
    PRIVATE = 'PRIVATE'


class ReactionType(models.TextChoices):
    LIKE = 'LIKE'
    HEART = 'HEART'
    SMILEY = 'SMILEY'


class User(models.Model):
    username = models.CharField(max_length=20, unique=True, blank=False)
    password = models.CharField(max_length=20)

    def __str__(self):
        return self.username


class Project(models.Model):
    title = models.CharField(max_length=20)
    description = models.CharField(max_length=160)
    licence = models.CharField(max_length=20)
    visibility = models.CharField(max_length=15, choices=Visibility.choices, default=Visibility.PRIVATE)
    link = models.CharField(max_length=50)
    lead = models.ForeignKey(User, on_delete=models.CASCADE)
    developers = models.ManyToManyField(to=User, blank=True, related_name="developers")
    starred = models.ManyToManyField(User, related_name="starred")

    def __str__(self):
        return "%s/%s" % (self.lead, self.title)

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'pk': self.pk})


class Label(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=10)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Milestone(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=120)
    due_date = models.DateTimeField
    state = models.CharField(max_length=20, choices=State.choices, default=State.OPEN)


class Task(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)
    assigned_to = models.ForeignKey(User, blank=True, null=True, related_name='assigned_to', on_delete=models.CASCADE)
    creator = models.ForeignKey(User, blank=False, related_name='creator', on_delete=models.CASCADE)


class Event(models.Model):
    date_time = models.DateTimeField(default=timezone.now)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)


class LabelApplication(Event):
    label = models.ManyToManyField(Label)


class UpdateEvent(Event):
    field_name = models.CharField(max_length=20)
    old_content = models.CharField(max_length=100)
    new_content = models.CharField(max_length=100)


class StateChange(Event):
    new_state = models.CharField(max_length=20)


class Comment(Event):
    content = models.CharField(max_length=2000)
    date_created = models.DateTimeField(default=timezone.now)


class Branch(models.Model):
    name = models.CharField(max_length=15)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)  # ManyToOne


class Commit(models.Model):
    date_time = models.DateTimeField(default=timezone.now)
    log_message = models.CharField(max_length=40)
    hash = models.CharField(max_length=30)
    author = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, blank=False, on_delete=models.CASCADE)


class Issue(Task):
    milestone = models.ForeignKey(Milestone, blank=True, null=True, on_delete=models.CASCADE)  # ManyToOne
    project = models.ForeignKey(Project, null=True, on_delete=models.CASCADE)
    is_open = models.BooleanField(default=True)

    def get_absolute_url(self):
        # print('AYOOOOOOOO',{'pk': self.project.id, 'ik': self.pk})
        return reverse('issue_detail', kwargs={'pk': self.project.id, 'ik': self.pk})

    def __str__(self):
        return "#%s - %s" % (self.id, self.title)


class PullRequest(Task):
    target = models.ForeignKey(Branch, blank=False, related_name='target', on_delete=models.CASCADE)
    source = models.ForeignKey(Branch, blank=False, related_name='source', on_delete=models.CASCADE)
    state = models.CharField(max_length=20, choices=State.choices, default=State.OPEN)


class Reaction(models.Model):
    type = ReactionType.choices
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
