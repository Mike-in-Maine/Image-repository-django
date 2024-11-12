from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import date
from .models import Photo, Tag, Category, Album
from .forms import TagForm, AlbumForm, AssignToAlbumForm
# Signup
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm
from django.contrib.auth import login
# Image manipulation
from PIL import Image, ExifTags
# OS stuff
import os
import calendar
import random
import datetime

def home(request):
    photos = Photo.objects.all()
    return render(request, 'index.html', {'photos': photos})
def index(request):
    # Query for the latest uploaded calendar day
    latest_day_photo = Photo.objects.latest('date_taken') if Photo.objects.exists() else None
    latest_date = latest_day_photo.date_taken if latest_day_photo else None

    # Fetch a random photo from all albums, if any exist
    random_album_photo = None
    if Photo.objects.exists():
        random_album_photo = random.choice(Photo.objects.all())

    context = {
        'latest_day_photo': latest_day_photo,
        'latest_date': latest_date,
        'random_album_photo': random_album_photo,
    }
    return render(request, 'home.html', context)


# PHOTO______________________________________________
@csrf_exempt
@login_required
def upload_photos(request):
    if request.method == 'POST' and request.FILES.getlist('photos'):
        for file in request.FILES.getlist('photos'):
            # Create a new Photo object for each uploaded file
            photo = Photo(
                image=file,
                user=request.user,  # Assuming your Photo model has a user field
                date_taken=datetime.datetime.now(),  # Set date_taken or extract it from EXIF if available
            )
            photo.save()

        return JsonResponse({'success': True, 'message': 'Photos uploaded successfully!'})
    return JsonResponse({'success': False, 'message': 'No photos to upload.'})
@login_required
def upload_page(request):
    return render(request, 'upload_pics_drag_drop.html')  # Render the upload page
@login_required
def photos_by_date(request, year, month, day):
    selected_date = date(year, month, day)
    # Filter photos and albums by the logged-in user
    photos = Photo.objects.filter(user=request.user, date_taken__date=selected_date)
    albums = Album.objects.filter(created_by=request.user).order_by('name')

    for photo in photos:
        photo.has_albums = photo.albums.exists()

    return render(request, 'photos_by_date.html', {'photos': photos, 'date': selected_date, 'albums': albums})
@login_required
def photo_detail(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    tags = photo.tags.all()  # Fetch all tags associated with the photo
    return render(request, 'photo_detail.html', {'photo': photo, 'tags': tags})
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

    # Get the referring page and redirect back to it
    referring_url = request.META.get('HTTP_REFERER')
    if referring_url:
        return redirect(referring_url)
    else:
        return redirect('home')  # Default fallback if referring URL is not available
@login_required
def rotate_photo(request, photo_id):
    if request.method == 'POST':
        photo = get_object_or_404(Photo, id=photo_id)
        direction = request.POST.get('direction')

        # Open the image file
        image_path = photo.image.path
        img = Image.open(image_path)

        # Determine rotation direction
        if direction == 'left':
            img = img.rotate(90, expand=True)  # Rotate left (90 degrees counterclockwise)
        elif direction == 'right':
            img = img.rotate(-90, expand=True)  # Rotate right (90 degrees clockwise)

        # Reset the EXIF orientation tag to normal (1)
        img = reset_exif_orientation(img)

        # Save the rotated image back to the same path
        img.save(image_path, quality=95)

        photo.create_thumbnail()
        photo.save()

        return redirect(request.META.get('HTTP_REFERER', 'calendar_view') + f"?nocache={photo_id}")
def reset_exif_orientation(img):
    """
    Resets the EXIF Orientation tag to '1' (default) after rotating the image.
    """
    if hasattr(img, '_getexif') and img._getexif():
        exif = img.info.get('exif', b'')  # Preserve existing EXIF data if available

        # Update the EXIF data with orientation reset
        exif_dict = img._getexif() or {}
        orientation_key = next((key for key, val in ExifTags.TAGS.items() if val == 'Orientation'), None)

        if orientation_key:
            exif_dict[orientation_key] = 1  # Set orientation to default (normal)

        # Re-save the image with the updated EXIF
        img.info['exif'] = exif

    return img
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

# CALENDAR____________________________________________
@login_required
def calendar_view(request, year=None, month=None):
    if year is None or month is None:
        now = timezone.now()
        year = now.year
        month = now.month

    # Filter photos by the selected year, month, and user
    photos_in_month = Photo.objects.filter(user=request.user, date_taken__year=year, date_taken__month=month)

    # Get distinct dates with photo counts for the logged-in user
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

# ALBUMS______________________________________________
@login_required
def view_album(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    photos = album.photos.all()  # Fetch photos related to the album
    return render(request, 'view_album.html', {'album': album, 'photos': photos})
@login_required
def create_album(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST)
        if form.is_valid():
            album = form.save(commit=False)  # Create an instance of the form, but don't save yet
            album.created_by = request.user  # Set the current user as the creator of the album
            album.save()  # Save the album instance with the created_by field
            return redirect('user_albums')  # Redirect to user's albums page after successful creation
    else:
        form = AlbumForm()

    return render(request, 'create_album.html', {'form': form})
@login_required
def user_albums(request):
    # Get the albums created by the currently logged-in user
    user_albums = Album.objects.filter(created_by=request.user)
    context = {
        'user_albums': user_albums,
    }
    return render(request, 'user_albums.html', context)
@login_required
def assign_to_album(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)

    if request.method == 'POST':
        form = AssignToAlbumForm(request.POST, instance=photo)

        if form.is_valid():
            # Get the selected album from the form and assign it
            selected_album = form.cleaned_data.get('albums')
            if selected_album:
                photo.albums.add(selected_album)  # Assign the photo to the selected album

                # Debug message to confirm the assignment
                print(f"Assigned photo '{photo.id}' to album '{selected_album.id}'")
                print(f"Photo '{photo.id}' is now in albums: {photo.albums.all()}")

                return redirect('photos_by_date', year=photo.date_taken.year, month=photo.date_taken.month,
                                day=photo.date_taken.day)
            else:
                messages.error(request, "Please select an album.")
        else:
            messages.error(request, "Form submission failed. Please try again.")

    # If the request is not POST or if the form submission fails, redirect to the home page
    return redirect('home')
@login_required
def delete_album(request, album_id):
    album = get_object_or_404(Album, id=album_id, created_by=request.user)  # Ensure only the creator can delete
    if request.method == 'POST':
        album.delete()
        messages.success(request, "Album deleted successfully.")
        return redirect('user_albums')
    return render(request, 'user_albums.html', {'user_albums': user_albums})


# AUTHENTICATION_____________________________________
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)  # Use UserCreationForm instead of SignUpForm
        if form.is_valid():
            form.save()

            # Send email notification
            send_mail(
                'Miky.pics: New Sign-Up Request',  # Subject
                'A new user has requested access.',  # Message
                'retiredtotuscany@gmail.com',  # From Email
                ['retiredtotuscany@gmail.com'],  # To Email
                fail_silently=False,
            )

            messages.success(request, 'Your sign-up request has been submitted.')
            return redirect('home')  # Redirect to a success page or 'home'
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})

def custom_login(request):
    return render(request, 'registration/login.html')
def custom_logout(request):
    return render(request, 'registration/logged_out.html')
