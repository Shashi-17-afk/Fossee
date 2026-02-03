from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.UploadCSVView.as_view()),
    path('summary/<int:dataset_id>/', views.SummaryView.as_view()),
    path('history/', views.HistoryView.as_view()),
    path('report/<int:dataset_id>/pdf/', views.ReportPDFView.as_view()),
]
