from django.urls import path
from .views import *

urlpatterns = [
    path('auth/register/', register_user, name='register'),
    path('auth/login/', login, name='login'),

    path('profile/', user_profile, name='user_profile'),

    path('status-icons/', task_status_icons, name='task_status_icons'),
    path('status-icons/<int:icon_id>/', task_status_icon_detail, name='task_status_icon_detail'),

    path('daily-lists/', daily_task_lists, name='daily_task_lists'),
    path('daily-lists/<int:list_id>/', daily_task_list_detail, name='daily_task_list_detail'),

    path('tasks/', tasks, name='tasks'),
    path('tasks/<int:task_id>/', task_detail, name='task_detail'),
    path('tasks/<int:task_id>/toggle/', toggle_task_completion, name='toggle_task_completion'),

    path('statistics/', task_statistics, name='task_statistics'),
    path('statistics/monthly-calendar/', monthly_calendar_statistics, name='monthly_calendar_statistics'),
]
