"""
URL configuration for workforce_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# OpenAPI / Swagger
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from drf_spectacular.renderers import OpenApiJsonRenderer

# Extra endpoint that forces JSON renderer so browser displays schema inline

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from app.views import RegisterView, WorkspaceViewSet

router = DefaultRouter()
router.register(r'workspaces', WorkspaceViewSet, basename='workspace')

urlpatterns = [
    path('admin/', admin.site.urls),
    # Schema generation
    path('api/schema/json/', SpectacularAPIView.as_view(), name='schema-json'),
    # Swagger UI
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema-json'), name='swagger-ui'),
    
    # Auth Endpoints
    path('api/auth/register/', RegisterView.as_view(), name='auth_register'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Workspace Endpoints (Router)
    path('api/', include(router.urls)),
]
