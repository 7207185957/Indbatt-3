from django.urls import path

from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportsHomeView.as_view(), name='home'),
    path('personnel/', views.PersonnelReportView.as_view(), name='personnel'),
    path('personnel/export/', views.PersonnelReportExportView.as_view(), name='personnel_export'),
    path('strength/', views.StrengthReportView.as_view(), name='strength'),
    path('strength/export/', views.StrengthReportExportView.as_view(), name='strength_export'),
    path('absence/', views.AbsenceReportView.as_view(), name='absence'),
    path('absence/export/', views.AbsenceReportExportView.as_view(), name='absence_export'),
    path('duty/', views.DutyReportView.as_view(), name='duty'),
    path('duty/export/', views.DutyReportExportView.as_view(), name='duty_export'),
    path('due-to-return/', views.DueToReturnReportView.as_view(), name='due_to_return'),
    path('due-to-return/export/', views.DueToReturnReportExportView.as_view(), name='due_to_return_export'),
]
