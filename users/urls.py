from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('manage_users/', views.manage_users, name='manage-users'),
    path('profile/', views.profile, name='profile'),
    path('admin_home/', views.admin_homepage, name='admin_home'),
    path('developer_home/', views.developer_homepage, name='developer_home'),
    path('project_manager_home/', views.project_manager_homepage, name='project_manager_home'),
]