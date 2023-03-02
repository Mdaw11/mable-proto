from django.urls import path
from . import views 

urlpatterns = [
    path('', views.home, name='home'),
    path('tickets/', views.ticket_home, name='ticket-home'),
    path('ticket/<int:pk>', views.ticket, name='ticket'),
    path('ticket_data/', views.get_ticket_data, name='ticket-data'),
    path('type_data/', views.get_type_data, name='type-data'),
    path('status_data/', views.get_status_data, name='status-data'),

    path('create-ticket/', views.createTicket, name='create-ticket'),
    path('update-ticket/<int:pk>/', views.updateTicket, name='update-ticket'),
    path('delete-ticket/<int:pk>/', views.deleteTicket, name='delete-ticket'),
    path('delete-message/<int:pk>/', views.deleteMessage, name='delete-message'),
    
    path('categories/', views.categoriesPage, name='categories'),
    path('activity/', views.activityPage, name='activity'),
]