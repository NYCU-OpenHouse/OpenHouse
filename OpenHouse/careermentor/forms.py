from django import forms
from . import models
from django.utils import timezone

class SignupForm(forms.ModelForm):
    required_css_class="required field"

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['mentor'].widget.attrs.update({
            'class': 'ui disabled dropdown',
        })
        self.fields['attend_mode'].widget.attrs.update({
            'class': 'ui dropdown',
        })
        self.fields['meal_category'].widget.attrs.update({
            'class': 'ui dropdown',
        })
        self.fields['time_available'].required = True

    class Meta:
        model=models.Signup
        fields='__all__'
        exclude=['id','updated','ps']
        widgets = {
            'question': forms.Textarea(attrs={'cols': 80, 'rows': 10}),
        }

    def save(self,commit=True):
        form = super(SignupForm, self).save(commit=False)
        if commit:
            form.save()
            return form

# Customized form for Career Seminar
class CareerSeminarSignupForm(forms.ModelForm):
    required_css_class="required field"

    def __init__(self, *args, **kwargs):
        super(CareerSeminarSignupForm, self).__init__(*args, **kwargs)
        self.fields['mentor'].widget.attrs.update({
            'class': 'ui disabled dropdown',
        })
        self.fields['attend_mode'].widget.attrs.update({
            'class': 'ui dropdown',
        })
        self.fields['meal_category'].widget.attrs.update({
            'class': 'ui dropdown',
        })
        set_attend_mode = models.Mentor.objects.get(id=kwargs['initial']['mentor']).set_attend_mode
        
        new_choices = list(self.fields['attend_mode'].choices)
        if set_attend_mode == '僅限實體':
            new_choices.remove(('線上', '線上(Online)'))
            self.fields['attend_mode'].initial = '實體'
        if set_attend_mode == '僅限線上':
            new_choices.remove(('實體', '實體(Onsite)'))
            self.fields['attend_mode'].initial = '線上'
        self.fields['attend_mode'].choices = new_choices
        self.fields['attend_mode'].widget.choices = new_choices

    class Meta:
        model=models.Signup
        fields='__all__'
        exclude=['id','updated','ps','time_available', 'question', 'cv_en', 'cv_zh', 'other']
        widgets = {
            'question': forms.Textarea(attrs={'cols': 80, 'rows': 10}),
        }

    def save(self,commit=True):
        form = super(CareerSeminarSignupForm, self).save(commit=False)
        if commit:
            form.save()
            return form