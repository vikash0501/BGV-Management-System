from .models import AuditLog


def create_audit_log(
    *,
    user=None,
    case=None,
    action,
    description
):
    return AuditLog.objects.create(
        user=user,
        case=case,
        action=action,
        description=description
    )