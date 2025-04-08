from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="ChatBot Psicológico API",
      default_version='v1',
      description="Documentación de la API del ChatBot Psicológico Adaptativo",
      terms_of_service="https://www.tusitio.com/terms/",
      contact=openapi.Contact(email="contacto@tusitio.com"),
      license=openapi.License(name="License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),  # Asegúrate de crear el archivo urls.py en la app "core"
    path('api/users/', include('users.urls')),
    path('api/chat/', include('chat.urls')),
    # Documentación con Swagger
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # Documentación con Redoc
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
