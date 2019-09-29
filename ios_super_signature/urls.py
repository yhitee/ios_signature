from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('background_manage/', admin.site.urls),
    path('',include('Linux_version.urls')),
]
