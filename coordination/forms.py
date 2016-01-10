from crispy_forms.bootstrap import StrictButton, PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML, Div, Row
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm, Form, ValidationError, ClearableFileInput
from django.forms.fields import CharField

from coordination.models import Quest, Mission, Hint, Message
from qc import settings


def clean_key(key):
    return key.replace(" ", "").lower()


class CustomClearableFileInput(ClearableFileInput):
    template_with_initial = (
        '%(initial_text)s картинка уже загружена. '
        '%(clear_template)s<br />%(input_text)s: %(input)s'
    )


class QuestForm(ModelForm):
    class Meta:
        model = Quest
        fields = ['title', 'start', 'description']

    def __init__(self, *args, **kwargs):
        super(QuestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.html5_required = True
        self.helper.layout = Layout(
            Field('title', autofocus=True),
            'start',
            'description'
        )


class MissionForm(ModelForm):
    class Meta:
        model = Mission
        fields = ['name', 'name_in_table', 'text', 'key', 'order_number']
        if settings.QC_UPLOAD:
            fields.append('picture')
            widgets ={
                'picture': CustomClearableFileInput,
            }

    def __init__(self, *args, **kwargs):
        next_number = kwargs.pop('next_number', None)
        super(MissionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.html5_required = True
        try:
            quest = self.instance.quest
        except ObjectDoesNotExist:
            quest = None
        simple_layout = Layout(
            HTML("<h2>{{ form.instance }}</h2>"),
            'text',
            'picture',
            Field('order_number', type="hidden"),
        )
        simple_fields = ['text', 'order_number']
        if self.instance.is_start:
            if quest.linear:
                self.Meta.fields = ['text', 'key', 'order_number']
                self.helper.layout = Layout(
                    HTML("<h2>{{ form.instance }}</h2>"),
                    'key',
                    'text',
                    'picture',
                    Field('order_number', type="hidden"),
                )
            elif quest.line_nonlinear:
                self.Meta.fields = simple_fields
                self.helper.layout = simple_layout
        elif self.instance.is_finish:
            if quest.linear:
                self.Meta.fields = simple_fields
                self.helper.layout = simple_layout
            elif quest.line_nonlinear:
                self.Meta.fields = ['name', 'text', 'key', 'order_number']
                self.helper.layout = Layout(
                    HTML("<h2>{{ form.instance }}</h2>"),
                    'name',
                    'key',
                    'text',
                    'picture',
                    Field('order_number', type="hidden"),
                )
        else:
            self.helper.layout = Layout(
                Row(
                    Div(Field('order_number', value=next_number),
                        css_class='col-xs-8 col-sm-3 col-md-4'),
                    Div('key', css_class='col-xs-12 col-sm-9 col-md-8')
                ),
                'name',
                'name_in_table',
                'text',
                'picture'
            )

    def clean_key(self):
        key = self.cleaned_data["key"]
        return clean_key(key)


class HintForm(ModelForm):
    class Meta:
        model = Hint
        fields = ['text', 'delay', 'order_number']

    def __init__(self, *args, **kwargs):
        next_number = kwargs.pop('next_number', None)
        super(HintForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.html5_required = True
        self.helper.layout = Layout(
            Row(
                Div(Field('order_number', value=next_number),
                    css_class='col-xs-6 col-sm-3 col-md-4'),
                Div('delay', css_class='col-xs-6 col-sm-3 col-md-4')
            ),
            Field('text', rows=4),
        )


class PlayerForm(Form):
    name = CharField(max_length=30, required=True)

    def __init__(self, *args, **kwargs):
        super(PlayerForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True
        self.helper.form_show_labels = False
        self.helper.form_class = 'form-inline col-md-8 col-md-offset-4'
        self.helper.layout = Layout(
            Field('name', autofocus=True, placeholder='Имя', size='45'),
            StrictButton('Добавить игрока', type='submit', css_class='btn-success')
        )


class KeyForm(Form):
    key = CharField(max_length=30, required=True)

    def __init__(self, *args, **kwargs):
        super(KeyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True
        self.helper.form_show_labels = False
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            PrependedText('key', '<span class="fa fa-key"></span>', placeholder='ключ', size='30'),
            StrictButton('Отправить', type='submit', css_class='btn-primary')
        )

    def clean_key(self):
        key = self.cleaned_data["key"]
        key_cleaned = clean_key(key)
        if len(key_cleaned) == 0:
            raise ValidationError("Пожалуйста введите хотя бы 1 символ.")
        return key_cleaned


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['text']

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.html5_required = True
        self.helper.layout = Layout(
            'text',
        )
