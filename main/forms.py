from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.forms import Form, CharField


class AuthForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            username = username.strip()
            password = password.strip()
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class NameChangeForm(Form):
    name = CharField(max_length=30, required=True)

    def __init__(self, *args, **kwargs):
        super(NameChangeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True
        self.helper.form_tag = False
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Field('name', autofocus=True, placeholder='Новое Имя', size='45'),
        )

    def clean_name(self):
        name = self.cleaned_data["name"]
        if not User.objects.filter(groups__name='organizers', first_name__iexact=name).exists():
            return name
        raise forms.ValidationError("Организатор с таким именем уже существует")
