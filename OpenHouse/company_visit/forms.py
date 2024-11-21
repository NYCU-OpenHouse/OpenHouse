from django import forms
from .models import StudentApply

class StudentApplyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StudentApplyForm, self).__init__(*args, **kwargs)
        self.fields['preferred_categories'].widget.attrs.update({
            'class': 'ui dropdown',
        })
    class Meta:
        model = StudentApply
        fields = '__all__'
        exclude = ['id']
