from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (RegisterSerializer, LoginSerializer, ProfileSerializer, ClientListSerializer,
)
from .models import User
from .permissions import IsAdmin, IsHR, IsVerifier, IsClient, IsCandidate

class RegisterView(generics.CreateAPIView):

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class LoginView(TokenObtainPairView):

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

class ProfileView(generics.RetrieveAPIView):

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class ClientListView(generics.ListAPIView):
    serializer_class = ClientListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(
            role=User.Role.CLIENT,
            is_active=True
        ).order_by('first_name', 'last_name')

class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {'detail': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {'detail': 'Logout successful.'},
                status=status.HTTP_205_RESET_CONTENT
            )

        except Exception:
            return Response(
                {'detail': 'Invalid or expired refresh token.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class AdminTestView(APIView):

    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({
            "message": "Welcome Admin!",
            "username": request.user.username,
            "role": request.user.role
        })

class HRTestView(APIView):

    permission_classes = [IsHR]

    def get(self, request):
        return Response({
            "message": "Welcome HR!",
            "username": request.user.username,
            "role": request.user.role
        })

class VerifierTestView(APIView):

    permission_classes = [IsVerifier]

    def get(self, request):
        return Response({
            "message": "Welcome Verifier!",
            "username": request.user.username,
            "role": request.user.role
        })

class ClientTestView(APIView):
    permission_classes = [IsClient]

    def get(self, request):
        return Response({
            "message": "Welcome Client!",
            "username": request.user.username,
            "role": request.user.role
        })

class CandidateTestView(APIView):
    permission_classes = [IsCandidate]

    def get(self, request):
        return Response({
            "message": "Welcome Candidate!",
            "username": request.user.username,
            "role": request.user.role
        })