from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar_url = models.CharField(max_length=255, blank=True, null=True)
    background_image = models.CharField(max_length=255, blank=True, null=True)
    sidebar_image = models.CharField(max_length=255, blank=True, null=True)
    theme_color = models.CharField(max_length=50, blank=True, null=True)
    font_size = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profile'

    def __str__(self):
        return f"Profile of {self.user_id.username}"


class TaskStatusIcon(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    status_name = models.CharField(max_length=50)
    icon_url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'task_status_icon'

    def __str__(self):
        return f"Icon {self.status_name} of {self.user_id.username}"


class DailyTaskList(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'daily_task_list'
        unique_together = ('user_id', 'date')

    def __str__(self):
        return f"Daily Task List for {self.user_id.username} on {self.date}"


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    list_id = models.ForeignKey(DailyTaskList, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    reminder = models.DateTimeField(blank=True, null=True)
    priority = models.IntegerField(default=0)
    status_icon_id = models.ForeignKey(TaskStatusIcon, on_delete=models.SET_NULL, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'task'

    def __str__(self):
        return self.title