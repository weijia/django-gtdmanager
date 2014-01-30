from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from datetimewidget.widgets import DateTimeWidget
from gtdmanager.models import Item, Context, Next, Reminder, Project
from django.core.exceptions import ValidationError

class ItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs:
            kwargs['instance'] = Item()
        super(ItemForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        
    class Meta:
        model = Item
        exclude = ('status',)

class ContextForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs:
            kwargs['instance'] = Context()
        super(ContextForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            'name',
            Submit('submit', 'Submit'),
        )

    class Meta:
        model = Context
        exclude = ('is_default',)

class ProjectForm(ItemForm):
    class Meta:
        model = Project
        exclude = ('status',)

    def clean(self):
        cleaned_data = super(ProjectForm, self).clean()
        parent_id = self.data.get('parent', None)
        if parent_id and int(parent_id) == self.instance.id:
            raise ValidationError('Cannot set parent to self')
        return cleaned_data

class NextForm(ItemForm):
    class Meta:
        model = Next
        exclude = ('status',)

class ReminderForm(ItemForm):
    class Meta:
        model = Reminder
        exclude = ('status',)
