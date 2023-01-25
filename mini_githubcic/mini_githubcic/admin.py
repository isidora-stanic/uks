from django.contrib import admin

from .models import User, Project, Issue, Branch, Label, Event

admin.site.register(User)
admin.site.register(Project)
admin.site.register(Issue)
admin.site.register(Branch)
admin.site.register(Label)
admin.site.register(Event)
