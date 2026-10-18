from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        'api/accounts/',
        include('accounts.urls')
    ),

    path(
        'api/candidates/',
        include('candidates.urls')
    ),

    path(
        'api/verifications/',
        include('verifications.urls')
    ),
    path(
        'api/documents/', include('documents.urls')
    ),
    path('api/reports/', include('reports.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/cases/', include('cases.urls')),
    path('api/audit-logs/',
         include('audit_logs.urls')),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)