from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager
from colorfield.fields import ColorField
from mini_githubcic.managers import GitUserManager
from ckeditor.fields import RichTextField


class State(models.TextChoices):
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
    MERGED = 'MERGED'


class Visibility(models.TextChoices):
    PUBLIC = 'PUBLIC'
    PRIVATE = 'PRIVATE'


class ReactionType(models.TextChoices):
    LIKE = 'LIKE'
    DISLIKE = 'DISLIKE'
    SMILE = 'SMILE'
    TADA = 'TADA'
    THINKING_FACE = 'THINKING_FACE'
    HEART = 'HEART'
    ROCKET = 'ROCKET'
    EYES = 'EYES'
    
    
class User(AbstractBaseUser):
    username = models.CharField(max_length=20, unique=True, blank=False)
    password = models.CharField(max_length=20)
    
    access_token = models.CharField(max_length=255, unique=False, blank=True, null=True)
    
    is_superuser = models.BooleanField(default=False)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_superuser
        
    USERNAME_FIELD = 'username'

    objects = GitUserManager()
    
    def __str__(self):
        return self.username
    
    class Meta:
        db_table = u'users'

    def get_absolute_url(self):
        return reverse('login')


class Project(models.Model): #todo pazi kod pull req, treba se ponuditi da se postavi na roditelja ako ima roditelja forkovanog
    title = models.CharField(max_length=20)
    description = models.CharField(max_length=160)
    licence = models.CharField(max_length=20)
    visibility = models.CharField(max_length=15, choices=Visibility.choices, default=Visibility.PRIVATE)
    link = models.CharField(max_length=50)
    lead = models.ForeignKey(User, on_delete=models.CASCADE)
    developers = models.ManyToManyField(to=User, blank=True, related_name="developers")
    starred = models.ManyToManyField(User, related_name="starred")
    watched = models.ManyToManyField(User, related_name="watched")
    fork_parent = models.ForeignKey('self', on_delete=models.CASCADE,  null=True) #mislim da ne treba da se kaskadira
    number_of_forked_project = models.DecimalField( max_digits=5, decimal_places=0, null=True)

    def __str__(self):
        return "%s/%s" % (self.lead, self.title)

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'pk': self.pk})

# class Repository(models.Model):
#     project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)  # mislim da ne treba da se kaskadira
#     fork_parent = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, related_name="forked_project")  # mislim da ne treba da se kaskadira
#     number_of_forked_project = models.DecimalField(max_digits=5, decimal_places=0, null=True)

class Label(models.Model):
    name = models.CharField(max_length=100)
    color = ColorField(default="#00000")
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('label_detail', kwargs={'pk': self.pk})


class Milestone(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=120)
    project = models.ForeignKey(Project, null=True, on_delete=models.CASCADE)
    due_date = models.DateTimeField(default=timezone.now)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return "%s" % (self.title)

    def get_absolute_url(self):
        return reverse('milestone_detail', kwargs={'pk': self.pk})


class Task(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)
    project = models.ForeignKey(Project, null=True, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, blank=True, null=True, related_name='assigned_to', on_delete=models.CASCADE)
    creator = models.ForeignKey(User, blank=False, related_name='creator', on_delete=models.CASCADE)
    labels = models.ManyToManyField(Label)


class Event(models.Model):
    date_time = models.DateTimeField(default=timezone.now)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    author = models.ForeignKey(User, blank=False, null=True, related_name='author', on_delete=models.CASCADE)


class LabelApplication(Event):
    label = models.ManyToManyField(Label)

class CreateEvent(Event):
    created_entity_type = models.CharField(max_length=20)
    
    def __str__(self):
        return "%s created this %s at %s" % (self.author, self.created_entity_type, str(self.date_time)[:-16])

class UpdateEvent(Event):
    field_name = models.CharField(max_length=20)
    old_content = models.CharField(max_length=100)
    new_content = models.CharField(max_length=100)

    def __str__(self):
        if self.field_name == 'is_open':
            if self.new_content.lower() == 'true':
                return "%s opened this issue at %s" % (self.author, str(self.date_time)[:-16])
            elif self.new_content.lower() == 'false':
                return "%s closed this issue at %s" % (self.author, str(self.date_time)[:-16])
            
        return "%s updated %s from %s to %s at %s" % (self.author, self.field_name, self.old_content, self.new_content, str(self.date_time)[:-16])

class Comment(Event):
    content = RichTextField(blank=True, null=True)
    


class Branch(models.Model):
    name = models.CharField(max_length=50)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)  # ManyToOne
    parent_branch = models.ForeignKey('self', null=True, on_delete=models.SET_NULL)

    def get_absolute_url(self):
        return reverse('branch_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return "%s" % (self.name)


class Commit(models.Model):
    date_time = models.DateTimeField(default=timezone.now)
    log_message = models.CharField(max_length=40)
    hash = models.CharField(max_length=30)
    author = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    branches = models.ManyToManyField(Branch, related_name='branches', blank=False, default=None)

    parents = models.ManyToManyField("self", symmetrical=False, blank=True, verbose_name=('Parent commits'))

    def get_absolute_url(self):
        return reverse('commit_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return "%s" % (self.hash[0:7])




class Issue(Task):
    milestone = models.ForeignKey(Milestone, blank=True, null=True, on_delete=models.CASCADE)  # ManyToOne
    is_open = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('issue_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return "#%s - %s" % (self.id, self.title)


class PullRequest(Task):
    target = models.ForeignKey(Branch, blank=False, related_name='target', on_delete=models.CASCADE)
    source = models.ForeignKey(Branch, blank=False, related_name='source', on_delete=models.CASCADE)
    state = models.CharField(max_length=20, choices=State.choices, default=State.OPEN)

    def get_absolute_url(self):
        return reverse('pull_request_detail', kwargs={'pk': self.pk})

class Reaction(models.Model):
    type = models.CharField(max_length=20, choices=ReactionType.choices, default=ReactionType.LIKE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

class Notification(models.Model): #razmisli o referenci na comit bukvalno
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, unique=False)  # OneToOne
    project = models.OneToOneField(Project, null=True, on_delete=models.CASCADE)
    is_reded = models.BooleanField(default=False)
    message = models.CharField(max_length=50, unique=False, blank=True)
    #object_id = models. mozda id od toga sto je