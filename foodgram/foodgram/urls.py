from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('recipes.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]