from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *
from django import forms

class ModelFormBase(forms.ModelForm):
    DISABLE = []
    LIMIT_QS = []
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.DISABLE:
            self.fields[field].disabled = True
        instance = kwargs.get('instance')
        if instance:
            for field in self.LIMIT_QS:
                qs = self.fields[field].queryset
                obj = getattr(instance,field,None)
                if obj:
                    self.fields[field].queryset = qs.filter(id=obj.pk)
                else:
                    self.fields[field].queryset = qs.none()
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(
            Button(
                'cancel', 'Cancel', css_class='btn-primary',
                onclick="history.back();"
            )
        )