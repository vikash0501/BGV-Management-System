from django.urls import path

from .views import AdminHRDashboardView, ClientDashboardView, VerifierDashboardView, CandidateDashboardView, RecentVerificationActivityView


urlpatterns = [
    path(
        'admin-hr/',
        AdminHRDashboardView.as_view(),
        name='admin_hr_dashboard'
    ),
    path('client/', ClientDashboardView.as_view(), name='client_dashboard'),
    path('verifier/',VerifierDashboardView.as_view(), name='verifier_dashboard'),
    path('candidate/',CandidateDashboardView.as_view(), name='candidate_dashboard'),
    path('recent-verifications/', RecentVerificationActivityView.as_view(), name='recent_verifications'),
]