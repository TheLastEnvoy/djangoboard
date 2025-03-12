# dashboard_so/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Adicione o namespace 'supervisao_ocupacional' aqui
    path('', include('supervisao_ocupacional.urls', namespace='supervisao_ocupacional')),
]
