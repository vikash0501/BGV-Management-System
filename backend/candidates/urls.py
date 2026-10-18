from django.urls import path

from .views import ( CandidateCreateView, CandidateListView, CandidateDetailView, CandidateClientAssignmentView, ClientCandidateListView,
CandidateMyProfileView,
)

urlpatterns = [
    path('', CandidateCreateView.as_view(), name='candidate_create'),
    path('list/', CandidateListView.as_view(), name='candidate_list'),
    path('my/',CandidateMyProfileView.as_view(), name='candidate_my_profile'),
    path('<int:pk>/', CandidateDetailView.as_view(), name='candidate_detail'),
    path('<int:pk>/assign-client/', CandidateClientAssignmentView.as_view(), name='candidate_assign_client'),
    path('client/my/',ClientCandidateListView.as_view(), name='client_my_candidates'),

]
