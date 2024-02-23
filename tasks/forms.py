from django import forms
from django.contrib.auth.forms import UsernameField, UserChangeForm, UserCreationForm, AuthenticationForm
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.utils.translation import gettext_lazy as _

from tasks.models import CustomUser
from tasks.utility_file import FileUtilities


class ASCIIUsernameField(UsernameField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(ASCIIUsernameValidator())


class UserSignupForm(UserCreationForm):
    """
        This form is used to create a new account for the user.
        """
    password1 = forms.CharField(label='Password',
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirm Password',
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ("username", "email")
        field_classes = {'username': ASCIIUsernameField}
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'eg: example_user'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'eg: example@gmail.com'}),
        }
        error_messages = {
            'username': {'required': 'Required. Please enter the username'},
            'email': {'required': 'Required. Please enter your email ID'},
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email__iexact=email).exists():
            self.add_error("email", _("A user with this email already exists."))
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if CustomUser.objects.filter(username__iexact=username).exists():
            self.add_error("username", _("A user with this username already exists."))
        return username


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")
        field_classes = {'username': ASCIIUsernameField}


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Email / Username', widget=forms.TextInput(
        attrs=
        {
            'placeholder': "Your email or username",
            'class': "input form-control"
        }
    ))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                 'class': 'input form-control'}))


class TasksHistoryDataForm(forms.Form):
    """
    This form is used to submit data from the users. It also validates that the data is correct.
    """
    text_data = forms.CharField(min_length=1,
                                max_length=1000,
                                label="Write Your Experience Here",
                                widget=forms.Textarea(attrs={'class': 'form-control', "rows": 6, "cols": 140}),
                                required=False)
    file_data = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
                                required=False,
                                label="Upload File Here")

    def clean(self):
        cleaned_text_data = self.cleaned_data['text_data']
        cleaned_file_data = self.cleaned_data['file_data']
        if cleaned_text_data == "" and cleaned_file_data is None:
            raise forms.ValidationError("Please share something.")
        elif cleaned_text_data != "" and cleaned_file_data is not None:
            raise forms.ValidationError("Please share either in writing or your images/audio/video.")
        if cleaned_file_data is not None and cleaned_text_data == "":
            valid_file_types = FileUtilities()
            original_file_name = cleaned_file_data.name
            file_extension = valid_file_types.get_file_extension(original_file_name)
            try:
                valid_file_types.get_file_type(file_extension)
            except ValueError:
                raise forms.ValidationError("This file is not supported.")

        return self.cleaned_data
