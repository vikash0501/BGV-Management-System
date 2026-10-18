from rest_framework import generics
from accounts.permissions import IsAdminOrHR
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.select_related(
        'user',
        'case'
    ).all()

    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminOrHR]

    def get_queryset(self):
        queryset = super().get_queryset()

        case_id = self.request.query_params.get('case')
        action = self.request.query_params.get('action')
        user_id = self.request.query_params.get('user')

        if case_id:
            queryset = queryset.filter(case_id=case_id)

        if action:
            queryset = queryset.filter(action=action)

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset