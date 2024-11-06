from django.urls import path 
from .views import send_message, list_messages
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('send', send_message, name='send_message'),
    path('', list_messages, name='list_messages'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)