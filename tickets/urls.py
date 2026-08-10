from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('ticket/new/', views.ticket_new, name='ticket_new'),
    path('ticket/<int:pk>/', views.ticket_detail, name='ticket_detail'),

    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/new/', views.admin_user_new, name='admin_user_new'),
    path('admin/users/<int:pk>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin/users/<int:pk>/delete/', views.admin_user_delete, name='admin_user_delete'),

    path('notifications/', views.notifications, name='notifications'),
    path('notifications/read-all/', views.notifications_read_all, name='notifications_read_all'),
    path('api/notifications/poll/', views.api_notifications_poll, name='api_notifications_poll'),
]
