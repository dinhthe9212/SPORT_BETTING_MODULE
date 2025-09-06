from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/sagas/', include('sagas.urls')),
    path('health/', include('sagas.urls')),
]

