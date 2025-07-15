from django.contrib import admin
from django.urls import path, include
from dashboard import views as dashboard_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_views.home, name='home'),
    path('register/', dashboard_views.register, name='register'),
    path('login/', dashboard_views.user_login, name='login'),
    path('logout/', dashboard_views.user_logout, name='logout'),
    path('dashboard/', include('dashboard.urls')),
    path('payment/', dashboard_views.payment, name='payment'),
]
