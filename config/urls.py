from django.contrib import admin
from django.urls import path, include  # ← добавить include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('', include('mailmaster.urls')),  # ← добавить эту строку
]
