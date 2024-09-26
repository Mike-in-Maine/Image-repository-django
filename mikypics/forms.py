from django import forms
from .models import Photo, Tag
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect


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

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login after successful signup
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})
