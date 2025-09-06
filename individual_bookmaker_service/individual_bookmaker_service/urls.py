"""
URL configuration cho Individual Bookmaker Service.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('individual_bookmaker.urls')),
    
    # Health check
    path('health/', include('individual_bookmaker.urls')),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site configuration
admin.site.site_header = 'Individual Bookmaker Service Administration'
admin.site.site_title = 'Bookmaker Admin'
admin.site.index_title = 'Welcome to Individual Bookmaker Service'
