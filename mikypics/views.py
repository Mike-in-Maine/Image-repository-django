from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import date
from .models import Photo, Tag
from .forms import TagForm
from django.contrib.auth.forms import UserCreationForm
import os
import calendar



def home(request):
    photos = Photo.objects.all()
    return render(request, 'index.html', {'photos': photos})

@login_required
def delete_photo(request, photo_id):
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

    return redirect('home')

@login_required
def calendar_view(request, year=None, month=None):
    if year is None or month is None:
        now = timezone.now()
        year = now.year
        month = now.month

    # Filter photos by the selected year and month
    photos_in_month = Photo.objects.filter(date_taken__year=year, date_taken__month=month)

    # Get distinct dates with photo counts
    dates_with_photos = photos_in_month.annotate(date=TruncDate('date_taken')).values('date').annotate(photo_count=Count('id'))

    # Create a dictionary to store photos per day (key: day of the month)
    photos_by_date = {entry['date'].day: entry['photo_count'] for entry in dates_with_photos}

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
        'photos_by_date': photos_by_date,  # Pass the dictionary of photos by day
    }
    return render(request, 'calendar_view.html', context)

@login_required
def photos_by_date(request, year, month, day):
    selected_date = date(year, month, day)
    photos = Photo.objects.filter(date_taken__date=selected_date)
    return render(request, 'photos_by_date.html', {'photos': photos, 'date': selected_date})
@login_required
def photo_detail(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    tags = photo.tags.all()  # Fetch all tags associated with the photo
    return render(request, 'photo_detail.html', {'photo': photo, 'tags': tags})
@login_required
def add_tags(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)

    if request.method == 'POST':
        form = TagForm(request.POST, instance=photo)
        if form.is_valid():
            form.save()
            return redirect('photos_by_date', year=photo.date_taken.year, month=photo.date_taken.month, day=photo.date_taken.day)
    else:
        form = TagForm(instance=photo)

    return render(request, 'add_tags.html', {'form': form, 'photo': photo})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def login(request):
    return render(request, 'registration/login.html')

def logout(request):
    return render(request, 'registration/logged_out.html')
