from django.shortcuts import render
from .models import Photo
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
import os
import calendar
from django.utils import timezone
from datetime import date

from mikypics.models import Photo
from django.db.models import DateField
from django.db.models import Count
from django.db.models.functions import TruncDate

def home(request):
    photos = Photo.objects.all()
    return render(request, 'index.html', {'photos': photos})

def delete_photo(request, photo_id):
    # Get the photo object from the database
    photo = get_object_or_404(Photo, id=photo_id)

    # Delete the original image
    if photo.image:
        image_path = os.path.join(settings.MEDIA_ROOT, photo.image.name)
        if os.path.exists(image_path):
            os.remove(image_path)

    # Delete the thumbnail
    if photo.thumbnail:
        thumbnail_path = os.path.join(settings.MEDIA_ROOT, photo.thumbnail.name)
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)

    # Delete the photo entry from the database
    photo.delete()

    # Redirect to the homepage or wherever you'd like
    return redirect('home')


def calendar_view(request, year=None, month=None):
    # If year or month is not provided, use the current month
    if year is None or month is None:
        now = timezone.now()
        year = now.year
        month = now.month

    # Get all distinct dates with photo counts
    dates_with_photos = Photo.objects.annotate(date=TruncDate('date_taken')).values('date').annotate(photo_count=Count('id'))

    # Create a dictionary to store photos per date
    photos_by_date = {entry['date']: entry['photo_count'] for entry in dates_with_photos}

    # Get a calendar for the given month
    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(year, month)

    # Calculate previous and next month/year
    prev_year = year if month > 1 else year - 1
    prev_month = month - 1 if month > 1 else 12
    next_year = year if month < 12 else year + 1
    next_month = month + 1 if month < 12 else 1

    context = {
        'month_days': month_days,
        'year': year,
        'month': month,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'photos_by_date': photos_by_date,
    }
    return render(request, 'calendar_view.html', context)

def photos_by_date(request, year, month, day):
    # Convert year, month, and day into a Python date object
    selected_date = date(year, month, day)

    # Get all photos taken on the specified date
    photos = Photo.objects.filter(date_taken__date=selected_date)

    return render(request, 'photos_by_date.html', {'photos': photos, 'date': selected_date})