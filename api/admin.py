from django.contrib import admin
from api.models import *
# Register your models here.
admin.site.register(UserProfile)
admin.site.register(TaskStatusIcon)
admin.site.register(DailyTaskList)
admin.site.register(Task)