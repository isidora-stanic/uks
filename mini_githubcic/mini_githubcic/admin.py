from django.contrib import admin

from .models import CreateEvent, LabelApplication, UpdateEvent, User, Project, Issue, Branch, Label, Comment

admin.site.register(User)
admin.site.register(Project)
admin.site.register(Issue)
admin.site.register(Branch)
admin.site.register(Label)
admin.site.register(CreateEvent)
admin.site.register(UpdateEvent)
admin.site.register(Comment)
admin.site.register(LabelApplication)

