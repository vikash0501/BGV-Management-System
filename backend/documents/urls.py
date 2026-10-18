from django.urls import path

from .views import (
    DocumentCreateView, DocumentListView, DocumentDetailView, DocumentVerificationView, MyDocumentListView, CandidateDocumentListView,
    ClientDocumentListView,
)

urlpatterns = [
    path(
        '',
        DocumentCreateView.as_view(),
        name='document_create'
    ),
    path(
        'list/', DocumentListView.as_view(), name='document_list'
    ),
    path(
        '<int:pk>/', DocumentDetailView.as_view(), name='decument_detail'
    ),
    path('<int:pk>/verify/', DocumentVerificationView.as_view(), name='document_verify'),
    path('my/',MyDocumentListView.as_view(), name='my_documents'),
    path('candidate/my/',CandidateDocumentListView.as_view(), name='candidate_my_documents'),
    path('client/my/', ClientDocumentListView.as_view(), name='client_my_documents'),
]