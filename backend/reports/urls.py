from django.urls import path

from .views import (
    ReportCreateView, ClientFinalReportListView, ClientReportDetailView, ClientReportVerificationView,ReportGenerateView,
    ClientStructuredReportView,
)

urlpatterns = [
    path(
        '',
        ReportCreateView.as_view(),
        name='report_create'
    ),
    path('client/my/',ClientFinalReportListView.as_view(), name='client_final_reports'),
    path('client/<int:pk>/', ClientReportDetailView.as_view(), name='client_report_detail'),
    path(
        'client/candidate/<int:candidate_id>/verifications/',ClientReportVerificationView.as_view(), name='client_report_verifications'
    ),
    path('<int:pk>/generate/', ReportGenerateView.as_view(), name='report_generate'),
    path('client/structured/<int:pk>/', ClientStructuredReportView.as_view(), name='client_structured_report'),
]