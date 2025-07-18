from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/add/', views.add_user, name='add_user'),
    path('admin/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('trainer/members/', views.view_assigned_members, name='view_assigned_members'),
    path('admin/assign_trainer/<int:user_id>/', views.assign_trainer, name='assign_trainer'),
    path('admin/generate_report/', views.generate_mock_report, name='generate_mock_report'),
    path('upload-plan/', views.upload_plan, name='upload_plan'),
    path('my-plans/', views.view_my_plans, name='view_my_plans'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    path('view-feedbacks/', views.view_feedbacks, name='view_feedbacks'),
    path('progress/', views.member_progress, name='member_progress'),

]