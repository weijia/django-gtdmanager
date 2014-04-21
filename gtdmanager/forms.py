from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from gtdmanager.models import Item, Context, Next, Reminder, Project
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

class ItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        action = None
        if 'instance' in kwargs and kwargs['instance'] is not None:
            action = reverse(self.Meta.updateView, args=(kwargs['instance'].id,))
        else:
            kwargs['instance'] = self.Meta.model()
            action = reverse(self.Meta.createView)

        addSubmit = kwargs.pop('addSubmit', True)

        super(ItemForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = action
        if addSubmit:
            self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Item
        exclude = ('status',)
        widgets = {
          'description': forms.Textarea(attrs={'rows':4, 'cols':15}),
        }
        createView = 'gtdmanager:item_create'
        updateView = 'gtdmanager:item_update'

class ContextForm(ItemForm):
    def __init__(self, *args, **kwargs):
        kwargs["addSubmit"] = False
        super(ContextForm, self).__init__(*args, **kwargs)
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            'name',
            Submit('submit', 'Submit'),
        )

    class Meta:
        model = Context
        exclude = ('is_default',)
        createView = 'gtdmanager:context_create'
        updateView = 'gtdmanager:context_update'

class ProjectForm(ItemForm):
    class Meta:
        model = Project
        exclude = ('status',)
        widgets = {
          'description': forms.Textarea(attrs={'rows':4, 'cols':15}),
        }
        createView = 'gtdmanager:project_create'
        updateView = 'gtdmanager:project_update'

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
        widgets = {
          'description': forms.Textarea(attrs={'rows':4, 'cols':15}),
        }
        createView = 'gtdmanager:next_create'
        updateView = 'gtdmanager:next_update'

class ReminderForm(ItemForm):
    class Meta:
        model = Reminder
        exclude = ('status',)
        widgets = {
          'description': forms.Textarea(attrs={'rows':4, 'cols':15}),
        }
        createView = 'gtdmanager:reminder_create'
        updateView = 'gtdmanager:reminder_update'
