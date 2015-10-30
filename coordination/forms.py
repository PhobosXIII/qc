from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django.forms import ModelForm
from coordination.models import Quest


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
