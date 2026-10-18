from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (RegisterView, LoginView, ProfileView, LogoutView, AdminTestView, HRTestView, VerifierTestView, ClientTestView, CandidateTestView,ClientListView,
)


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/',LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('admin-test/',AdminTestView.as_view(), name='admin_test'),
    path('hr-test/',HRTestView.as_view(), name='hr_test'),
    path('verifier-test', VerifierTestView.as_view(), name='verifier_test'),
    path('client-test/',ClientTestView.as_view(), name='client_test'),
    path('candidate-test/', CandidateTestView.as_view(), name='candidate_test')
]