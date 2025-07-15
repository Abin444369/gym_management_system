from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/add/', views.add_user, name='add_user'),
    path('admin/delete/<int:user_id>/', views.delete_user, name='delete_user'),
]
