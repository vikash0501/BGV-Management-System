from django.urls import path, include

from .views import (
    VerificationCreateView, VerificationListView, VerificationDetailView, VerificationAssignmentView,
    MyVerificationListView,
    VerificationProcessView,
    ClientVerificationListView,
)

urlpatterns = [
    path(
        '',
        VerificationCreateView.as_view(),
        name='verification_create'
    ),
    path(
        'list/',
        VerificationListView.as_view(),
        name='verification_list'
    ),
    path(
        '<int:pk>/',
        VerificationDetailView.as_view(),
        name='verification_detail'
    ),
    path(
        '<int:pk>/assign/',
        VerificationAssignmentView.as_view(),
        name='verification_assign'
    ),
    path(
        'my/',
        MyVerificationListView.as_view(),
        name='my_verifications',
    ),
    path(
        '<int:pk>/process/',
        VerificationProcessView.as_view(),
        name='verification_process'
    ),
    path('client/my/', ClientVerificationListView.as_view(), name='client_my_verifications'),
]