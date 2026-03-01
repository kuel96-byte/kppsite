from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('scan/', views.scan_qr, name='scan_qr'),
    path('logs/', views.logs, name='logs'),
    path('generate-qr/<int:pass_id>/', views.generate_qr, name='generate_qr'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)