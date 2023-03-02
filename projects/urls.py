from django.urls import path
from . import views

urlpatterns = [
    path('projects/', views.project_home, name='project-home'),
    path('projects/<int:pk>/', views.project, name='project'),
    
    path('create-project/', views.createProject, name='create-project'),
    path('update-project/<int:pk>/', views.updateProject, name='update-project'),
    path('delete-project/<int:pk>/', views.deleteProject, name='delete-project'),
]