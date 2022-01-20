from django import forms
from .models import Item, Character, ItemList
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UploadFileForm(forms.Form):
    file = forms.FileField(allow_empty_file=False)
    character = forms.ChoiceField()

    def __init__(self, user):
        super(UploadFileForm, self).__init__()
        chars = Character.objects.filter(user=user)
        self.fields["character"].choices = ((ch.id, ch.name) for ch in chars)


class AddItemForm(forms.ModelForm):
    # file = forms.FileField(allow_empty_file=True, required=False)

    class Meta:
        model = Item
        fields = ["character",
                  # "name",
                  "mythic",
                  "reaper"]

    def __init__(self, user):
        super().__init__()
        character = forms.ModelChoiceField(queryset=Character.objects.filter(user=user), )
        # name = forms.ModelChoiceField(queryset=ItemList.objects.all())

        self.fields["character"].queryset = Character.objects.filter(user=user)

        self.fields["character"].widget.attrs.update({"class": "form-control dropdown", "data-live-search": "true"})
        # self.fields["name"].widget.attrs.update({"class": "form-control", "data-live-search": "true"})
        self.fields["mythic"].widget.attrs.update({"class": "form-control"})
        self.fields["reaper"].widget.attrs.update({"class": "form-control"})
        # self.fields["file"].widget.attrs.update({"class": "form-control"})

        # self.fields["name"].required = False
        self.fields["mythic"].required = False
        self.fields["reaper"].required = False
        self.fields["character"].required = True
        # self.fields["file"].required = False


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["email"].widget.attrs.update({"class": "form-control"})
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CreateCharacterForm(forms.Form):
    char_name = forms.CharField(max_length=32)


class DeleteCharacterForm(forms.ModelForm):

    class Meta:
        model = Character
        fields = ["id", "name"]

    def __init__(self, user):
        super(DeleteCharacterForm, self).__init__()
        self.fields["name"] = forms.ModelChoiceField(queryset=Character.objects.filter(user=user))