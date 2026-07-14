from django.urls import path

from . import views

app_name = 'strength'

urlpatterns = [
    path('', views.DailyStrengthListView.as_view(), name='list'),
    path('summary/', views.StrengthSummaryView.as_view(), name='summary'),
    path('add/', views.DailyStrengthCreateView.as_view(), name='add'),
    path('<int:pk>/', views.DailyStrengthDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.DailyStrengthUpdateView.as_view(), name='edit'),
]
