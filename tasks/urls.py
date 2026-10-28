

from django.urls import path

from tasks.views import complete_task, create_task, delete_task, get_task_colors, get_tasks, incomplete_task, update_task, verify_and_complete_task 



urlpatterns = [
    path("create/", create_task, name="create-task"),
    path("gettaskq/", get_tasks, name="get-task"),
    path("complete/<str:task_id>/", complete_task, name="complete-task"),
    path("incomplete/<str:task_id>/", incomplete_task, name="incomplete-task"),
    path("delete/<str:task_id>/", delete_task, name="delete_task"),
    path("update/<str:task_id>/", update_task, name="delete_task"),
    path('colors/', get_task_colors, name='get_task_colors'),
    path("verify_and_complete/<str:task_id>/", verify_and_complete_task, name="verify-and-complete-task"),

    ]