from django.urls import path

from . import views

app_name = 'dutyroster'

urlpatterns = [
    path('', views.DutyRosterListView.as_view(), name='list'),
    path('upcoming/', views.UpcomingDutyListView.as_view(), name='upcoming'),
    path('add/', views.DutyRosterCreateView.as_view(), name='add'),
    path('<int:pk>/', views.DutyRosterDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.DutyRosterUpdateView.as_view(), name='edit'),
]
