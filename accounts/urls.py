from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/add/', views.UserCreateView.as_view(), name='user_add'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/password/', views.SetUserPasswordView.as_view(), name='user_password'),
    path('my-password/', views.MyPasswordChangeView.as_view(), name='my_password'),
]
