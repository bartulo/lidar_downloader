from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from webapp.views import MapView

app_name = 'webapp'

urlpatterns = [
    path("map/", MapView.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
