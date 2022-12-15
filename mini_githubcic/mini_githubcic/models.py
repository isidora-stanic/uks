from django.db import models
    
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
    
class Label(models.Model):
    name=models.CharField(max_length=20)
    
class User(models.Model):
    username=models.CharField(max_length=20)
    password=models.CharField(max_length=20)

class Task(models.Model):
    assigned_to=models.ForeignKey(User, blank=True)
    creator=models.ForeignKey(User, blank=False)  

class Event(models.Model):
    date_time=models.DateTimeField  
    task=models.Model(Task)
    
class LabelApplication(Event):
    label=models.ManyToManyField(Label)

class UpdateEvent(Event):
    field_name=models.CharField(max_length=20)
    old_content=models.CharField(max_length=100)
    new_content=models.CharField(max_length=100)
    
class StateChange(Event):
    new_state=models.CharField(max_length=20)
    
class Comment(Event):
    content=models.CharField(max_length=200)
    date_created=models.DateTimeField

class Branch(models.Model):
    name=models.CharField(max_length=15)

class Commit(models.Model):
    date_time=models.DateTimeField
    log_message=models.CharField(max_length=40)
    hash=models.CharField(max_length=30)
    author=models.ForeignKey(User, blank=False)
    branch=models.ForeignKey(Branch, blank=False)
    
class Milestone(models.Model):
    title=models.CharField(max_length=30)
    description=models.CharField(max_length=120)
    due_date=models.DateTimeField
    state=models.CharField(choices=State.choices, default=State.OPEN)
    tasks=models.ManyToOneRel(Task, blank=True)

class Issue(Task):
    title=models.CharField(max_length=30)
    description=models.CharField(max_length=120)
    date_created=models.DateTimeField
    
class Pull_request(Task):
    target=models.ForeignKey(Branch, blank=False)
    source=models.ForeignKey(Branch, blank=False)
    
class Reaction(models.Model):
    type=models.Choices(choices=ReactionType.choices)
    user=models.ForeignKey(User)
    comment=models.ForeignKey(Comment)
    
class Project(models.Model):
    title=models.CharField(max_length=20)
    description=models.CharField(max_length=160)
    licence=models.CharField(max_length=20)
    visibility=models.Choices(choices=Visibility.choices, default=Visibility.PRIVATE)
    link=models.CharField(max_length=50)
    lead=models.ForeignKey(User)
    labels=models.ManyToOneRel(Label)
    developers=models.ManyToOneRel(User)
    starred=models.ManyToOneRel(User)
    branches=models.ManyToOneRel(Branch, blank=False)
    