from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import Textarea


class ContactForm(forms.Form):
    subject = forms.CharField(label='Тема', max_length=100, required=True)
    sender = forms.EmailField(label='Ваш e-mail')
    message = forms.CharField(label='Сообщение', required=True, widget=Textarea())

    def __init__(self, *args, **kwargs):
        subj_code = int(kwargs.pop('subj_code', 0))
        subj = None
        help = None
        if subj_code == 1:
            subj = 'Получить аккаунт организатора'
            help = 'Обязательно укажите имя, ник или команду'
        super(ContactForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True
        self.helper.form_class = 'col-md-6 col-md-offset-3'
        if subj:
            self.helper.layout = Layout(
                Field('subject', value=subj),
                Field('sender', autofocus=True),
                Field('message', placeholder=help),
                StrictButton('Отправить', type='submit', css_class='btn-primary')
            )
        else:
            self.helper.layout = Layout(
                Field('subject', autofocus=True),
                'sender',
                'message',
                StrictButton('Отправить', type='submit', css_class='btn-primary')
            )


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
