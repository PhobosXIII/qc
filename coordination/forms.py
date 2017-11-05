from crispy_forms.bootstrap import StrictButton, PrependedText, FieldWithButtons
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML, Div, Row
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail.backends import console
from django.forms import ModelForm, Form, ValidationError, ClearableFileInput, ModelChoiceField
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
        fields = ['title', 'start', 'description', 'game_over', 'order_number']

    def __init__(self, *args, **kwargs):
        type = kwargs.pop('type', None)
        parent = kwargs.pop('parent', None)
        super(QuestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.html5_required = True
        if type:
            self.instance.type = type
        if parent:
            self.instance.parent = parent
        quest = self.instance
        if quest.parent:
            next_number = quest.parent.next_line_number()
            self.Meta.fields = ['title', 'order_number']
            self.helper.layout = Layout(
                    Row(
                        Div(Field('order_number', value=next_number, min=1), css_class='col-xs-7 col-sm-3 col-md-4'),
                    ),
                    Field('title', autofocus=True),
                )
        else:
            if quest.nonlinear or quest.multilinear:
                self.helper.layout = Layout(
                    Field('title', autofocus=True),
                    'start',
                    'game_over',
                    'description',
                    Field('order_number', type="hidden"),
                )
            else:
                self.Meta.fields = ['title', 'start', 'description', 'order_number']
                self.helper.layout = Layout(
                    Field('title', autofocus=True),
                    'start',
                    'description',
                    Field('order_number', type="hidden"),
                )


class MissionForm(ModelForm):
    class Meta:
        model = Mission
        fields = ['name', 'name_in_table', 'text', 'key', 'order_number', 'points']
        if settings.QC_UPLOAD:
            fields.append('picture')
            widgets = {
                'picture': CustomClearableFileInput,
            }

    def __init__(self, *args, **kwargs):
        quest_arg = kwargs.pop('quest', None)
        super(MissionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.html5_required = True
        mission = self.instance
        try:
            quest = mission.quest
        except ObjectDoesNotExist:
            quest = quest_arg

        simple_layout = Layout(
            HTML("<h2>{{ form.instance }}</h2>"),
            'text',
            'picture',
            Field('order_number', type="hidden"),
            Field('points', type="hidden"),
        )
        simple_fields = ['text', 'order_number']
        if mission.is_start:
            if quest.linear:
                self.Meta.fields = ['text', 'key', 'order_number']
                self.helper.layout = Layout(
                    HTML("<h2>{{ form.instance }}</h2>"),
                    'key',
                    'text',
                    'picture',
                    Field('order_number', type="hidden"),
                    Field('points', type="hidden"),
                )
            else:
                self.Meta.fields = simple_fields
                self.helper.layout = simple_layout
        elif mission.is_finish:
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
                    Field('points', type="hidden"),
                )
            elif quest.nonlinear or quest.multilinear:
                self.Meta.fields = simple_fields
                self.helper.layout = Layout(
                    HTML("<h2>{{ form.instance }}</h2>"),
                    'text',
                    Field('order_number', type="hidden"),
                    Field('points', type="hidden"),
                )
        else:
            next_number = quest.next_mission_number()
            if quest.nonlinear or quest.parent:
                self.helper.layout = Layout(
                    Row(
                        Div(Field('order_number', value=next_number, min=1),
                            css_class='col-xs-7 col-sm-3 col-md-4'),
                        Div('points', css_class='col-xs-5 col-sm-3 col-md-3'),
                        Div('key', css_class='col-xs-12 col-sm-6 col-md-5')
                    ),
                    'name',
                    'name_in_table',
                    'text',
                    'picture'
                )
            else:
                self.helper.layout = Layout(
                    Row(
                        Div(Field('order_number', value=next_number, min=1),
                            css_class='col-xs-8 col-sm-3 col-md-4'),
                        Div('key', css_class='col-xs-12 col-sm-9 col-md-8')
                    ),
                    'name',
                    'name_in_table',
                    'text',
                    'picture',
                    Field('points', type="hidden"),
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
            'text',
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
        quest = kwargs.pop('quest', None)
        super(KeyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True
        self.helper.form_show_labels = False
        self.helper.form_class = 'form-inline'
        if quest.nonlinear:
            self.helper.form_tag = False
            self.helper.layout = Layout(
                FieldWithButtons(Field('key', placeholder='ключ', size='30'),
                                 StrictButton('OK', type='submit', css_class='btn-primary')),
            )
        else:
            if quest.multilinear:
                self.helper.form_tag = False
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


class OrganizerForm(Form):
    organizer = ModelChoiceField(queryset=None, empty_label='Выберите организатора', required=True)

    def __init__(self, *args, **kwargs):
        organizers = kwargs.pop('organizers')
        super(OrganizerForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True
        self.helper.form_show_labels = False
        self.helper.form_class = 'form-inline col-md-8 col-md-offset-4'
        self.fields['organizer'].queryset = organizers
        self.helper.layout = Layout(
            Field('organizer', autofocus=True, placeholder='Выберете организатора'),
            StrictButton('Добавить', type='submit', css_class='btn-success')
        )
