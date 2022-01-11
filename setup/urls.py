from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('contas.urls')),
    path('', include('dashboard.urls')),
    path('', include('acoes.urls')),
]
