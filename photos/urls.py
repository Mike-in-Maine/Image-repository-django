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
from django.contrib.auth import views as auth_views
from django.urls import path, include

from mikypics import views  # This is correct if `views.py` exists in the same directory.
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView



urlpatterns = [
                  # Authentication (Django wants this structure, dont modify it)
                  path('73B16/', admin.site.urls),
                  path('accounts/', include('django.contrib.auth.urls')),
                  #path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
                  #path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),  # Add this if you want both paths
                  path('', views.home, name='home'),

                  # Photo Actions
                  path('upload-photos/', views.upload_photos, name='upload_photos'),
                  path('upload/', views.upload_page, name='upload_page'),
                  path('delete-photo/<int:photo_id>/', views.delete_photo, name='delete_photo'),
                  path('rotate-photo/<int:photo_id>/', views.rotate_photo, name='rotate_photo'),

                  # Calendar views
                  path('calendar_view', views.calendar_view, name='calendar_view'),
                  path('calendar_view/<int:year>/<int:month>/', views.calendar_view, name='calendar_view_with_date'),

                  # Calendar with year and month for a specific date
                  path('photos/<int:year>/<int:month>/<int:day>/', views.photos_by_date, name='photos_by_date'),

                  # Add tags to a photo
                  path('add-tags/<int:photo_id>/', views.add_tags, name='add_tags'),

                  # Albums
                  path('create-album/', views.create_album, name='create_album'),  # Ensure this exists
                  path('assign-to-album/<int:photo_id>/', views.assign_to_album, name='assign_to_album'),
                  path('user-albums/', views.user_albums, name='user_albums'),
                  path('album/<int:album_id>/', views.view_album, name='view_album'),
                  path('album/<int:album_id>/delete/', views.delete_album, name='delete_album'),

                  ## Authentication and signup
                  path('login/', auth_views.LoginView.as_view(), name='login'),
                  path('logout/', LogoutView.as_view(), name='logout'),
                  path('signup/', views.signup, name='signup'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


