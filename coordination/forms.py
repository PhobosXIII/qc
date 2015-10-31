from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML, Div, Hidden, Row
from django.forms import ModelForm
from coordination.models import Quest, Mission


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
        fields = ['name', 'name_in_table', 'text', 'picture', 'key', 'order_number']

    def __init__(self, *args, **kwargs):
        next_number = kwargs.pop('next_number', None)
        super(MissionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.html5_required = True
        if self.instance.is_start:
            self.Meta.fields = ['text', 'key', 'order_number']
            self.helper.layout = Layout(
                HTML("<h2>{{ form.instance }}</h2>"),
                'key',
                'text',
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
                'picture',
            )
