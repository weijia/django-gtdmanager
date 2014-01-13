from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from gtdmanager.models import Item

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