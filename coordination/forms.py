from crispy_forms.bootstrap import StrictButton, PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML, Div, Row
from django.forms import ModelForm, Form
from django.forms.fields import CharField
from coordination.models import Quest, Mission, Hint


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
        fields = ['name', 'name_in_table', 'text', 'media_file', 'key', 'order_number']

    def __init__(self, *args, **kwargs):
        next_number = kwargs.pop('next_number', None)
        super(MissionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.html5_required = True
        if self.instance.is_start:
            self.Meta.fields = ['text', 'media_file', 'key', 'order_number']
            self.helper.layout = Layout(
                HTML("<h2>{{ form.instance }}</h2>"),
                'key',
                'text',
                'media_file',
                Field('order_number', type="hidden"),
            )
        elif self.instance.is_finish:
            self.Meta.fields = ['text', 'media_file', 'order_number']
            self.helper.layout = Layout(
                HTML("<h2>{{ form.instance }}</h2>"),
                'text',
                'media_file',
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
                'media_file',
            )


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
    name = CharField(max_length=100, required=True)

    def __init__(self, *args, **kwargs):
        super(PlayerForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.html5_required = True
        self.helper.form_show_labels = False
        self.helper.form_class = 'form-inline col-md-8 col-md-offset-4'
        self.helper.layout = Layout(
            Field('name', autofocus=True, placeholder='Имя', size='50'),
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
            HTML('<p class="alert alert-warning">Ключ вводится маленькими буквами, без пробелов и дефисов.</p>'),
            PrependedText('key', '<span class="fa fa-key"></span>', autofocus=True, placeholder='ключ', size='30'),
            StrictButton('Отправить', type='submit', css_class='btn-primary')
        )
