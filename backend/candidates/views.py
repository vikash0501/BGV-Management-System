from rest_framework import generics
from accounts.permissions import IsAdminOrHR
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .models import Candidate
from .serializers import CandidateSerializer, CandidateClientAssignmentSerializer
from accounts.permissions import IsAdminOrHR, IsClient, IsCandidate
class CandidateCreateView(generics.CreateAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [IsAdminOrHR]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class CandidateListView(generics.ListAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [IsAdminOrHR]

    filter_backends = [DjangoFilterBackend,
                       SearchFilter,
                       ]

    filterset_fields = [
        'candidate_code',
        'email',
        'phone',
        'city',
        'state',
        'status',
    ]

    search_fields = [
        'candidate_code',
        'first_name',
        'last_name',
        'email',
        'phone',
        'city',
        'state',
    ]

class CandidateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [IsAdminOrHR]

class CandidateMyProfileView(generics.RetrieveAPIView):
    serializer_class=CandidateSerializer
    permission_classes=[IsCandidate]

    def get_object(self):
        return Candidate.objects.get(
            user =self.request.user
        )

class CandidateClientAssignmentView(generics.UpdateAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateClientAssignmentSerializer
    permission_classes = [IsAdminOrHR]

class ClientCandidateListView(generics.ListAPIView):
    serializer_class = CandidateSerializer
    permission_classes = [IsClient]

    def get_queryset(self):
        return Candidate.objects.filter(
            client=self.request.user
        )
