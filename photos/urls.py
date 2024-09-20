"""
URL configuration for photos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from mikypics import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('delete-photo/<int:photo_id>/', views.delete_photo, name='delete_photo'),
    path('calendar_view/', views.calendar_view, name='calendar_view'),  # Homepage with calendar
    path('calendar_view/<int:year>/<int:month>/', views.calendar_view, name='calendar_view_with_date'),  # Calendar with year and month
    path('photos/<int:year>/<int:month>/<int:day>/', views.photos_by_date, name='photos_by_date'),  # Photos for a specific date
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


