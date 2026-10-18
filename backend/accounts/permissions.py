from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    message = "Only Admin users are allowed."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "ADMIN"
        )


class IsHR(BasePermission):
    message = "Only HR users are allowed."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "HR"
        )


class IsVerifier(BasePermission):
    message = "Only Verifier users are allowed."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "VERIFIER"
        )


class IsClient(BasePermission):
    message = "Only Client users are allowed."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "CLIENT"
        )


class IsCandidate(BasePermission):
    message = "Only Candidate users are allowed."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "CANDIDATE"
        )

class IsAdminOrHR(BasePermission):
    message = "Only Admin or HR users are allowed."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ["ADMIN", "HR"]
        )