from django.urls import path

from . import views

app_name = 'absence'

urlpatterns = [
    path('', views.AbsenceListView.as_view(), name='list'),
    path('due-to-return/', views.DueToReturnListView.as_view(), name='due_to_return'),
    path('add/', views.AbsenceCreateView.as_view(), name='add'),
    path('<int:pk>/', views.AbsenceDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.AbsenceUpdateView.as_view(), name='edit'),
]
