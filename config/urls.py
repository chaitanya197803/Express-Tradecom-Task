from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('', RedirectView.as_view(url='swagger/', permanent=False)),
    path('admin/', admin.site.urls),
    # OpenAPI Schema / Swagger UI / Redoc
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Users routes
    path('users', include('users.routes.user_routes')),
    path('users/', include('users.routes.user_routes')),
]

