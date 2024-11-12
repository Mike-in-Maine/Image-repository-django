from .models import Photo, Tag, Album
from django.shortcuts import render, redirect, get_object_or_404

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['name', 'description']

class AssignToAlbumForm(forms.ModelForm):
    albums = forms.ModelChoiceField(queryset=Album.objects.all(), required=True)  # Using ModelChoiceField for a single selection

    class Meta:
        model = Photo
        fields = ['albums']

class TagForm(forms.ModelForm):
    # Allow multiple tags to be selected/added
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    new_tag = forms.CharField(max_length=50, required=False, help_text="Add a new tag")

    class Meta:
        model = Photo
        fields = ['tags']  # Only tags field will be shown

    def save(self, commit=True):
        instance = super(TagForm, self).save(commit=False)
        new_tag = self.cleaned_data.get('new_tag')

        if new_tag:
            # Create and add the new tag
            tag, created = Tag.objects.get_or_create(name=new_tag)
            instance.tags.add(tag)

        if commit:
            instance.save()
        return instance

def add_tags(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    if request.method == "POST":
        form = TagForm(request.POST, instance=photo)
        if form.is_valid():
            form.save()
            return redirect('photos_by_date', year=photo.date_taken.year, month=photo.date_taken.month, day=photo.date_taken.day)
    else:
        form = TagForm(instance=photo)
    return render(request, 'add_tags.html', {'form': form, 'photo': photo})
