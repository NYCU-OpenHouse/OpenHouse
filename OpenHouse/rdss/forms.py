from django import forms
import rdss.models
from django.utils import timezone


class SignupCreationForm(forms.ModelForm):
    required_css_class = 'required field'

    def __init__(self, *args, **kwargs):
        super(SignupCreationForm, self).__init__(*args, **kwargs)
        self.fields['zone'].widget.attrs.update({
            'class': 'ui dropdown',
        })
        self.fields['history'].widget.attrs.update({
            'class': 'ui dropdown',
        })
        self.fields['seminar'].widget.attrs.update({
            'class': 'ui dropdown',
        })
        self.fields['seminar_type'].widget.attrs.update({
            'class': 'ui dropdown',
        })
        self.fields['seminar_ece'].widget.attrs.update({
            'class': 'ui dropdown',
        })
        self.fields['jobfair'].widget.attrs.update({
            'max' : '4',
            'min' : '0'
        })

    class Meta:
        model = rdss.models.Signup
        fields = '__all__'
        exclude = ['payment', 'receipt_no', 'ps']

    def save(self, commit=True):
        record = super(SignupCreationForm, self).save(commit=False)
        if commit:
            record.save()
        return record


class SeminarInfoCreationForm(forms.ModelForm):
    class Meta:
        model = rdss.models.SeminarInfo
        fields = '__all__'
        exclude = ['cid', 'attendees', 'snack_box']

    def __init__(self, *args, **kwargs):
        super(SeminarInfoCreationForm, self).__init__(*args, **kwargs)
        self.fields['contact_mobile'].widget.attrs.update({
            'placeholder': '格式：0912-345678',
        })

    # def clean_cid(self):
    #       raise forms.ValidationError(
    #               self.error_messages['cid_error'],
    #               code='cid_error'
    #               )
    #       return cid

    def save(self, commit=True):
        record = super(SeminarInfoCreationForm, self).save(commit=False)
        if commit:
            record.save()
        return record


class JobfairInfoCreationForm(forms.ModelForm):
    class Meta:
        model = rdss.models.JobfairInfo
        fields = '__all__'
        exclude = ['company']

    def __init__(self, *args, max_num=None, **kwargs):
        # (2025 recruit) The default value of total lunchbox is ${max_num * 3} meal_lunchbox.
        initial_data = kwargs.pop('initial', {})
        default_meat_lunchbox = initial_data.get('meat_lunchbox', max_num*3)

        super(JobfairInfoCreationForm, self).__init__(*args, **kwargs)
        # Set default values
        if not self.instance.pk or not self.instance.meat_lunchbox:
            self.fields['meat_lunchbox'].initial = default_meat_lunchbox
        # Set attributes max and min
        self.fields['lunch_box'].widget.attrs.update({
            'max' : max_num*3,
            'min' : '0'
        })
        self.fields['parking_tickets'].widget.attrs.update({
            'max' : max_num*2,
            'min' : '0'
        })
        self.fields['contact_mobile'].widget.attrs.update({
            'placeholder': '格式：0912-345678',
        })
        self.fields['meat_lunchbox'].widget.attrs.update({
            'max' : max_num*3,
            'min' : '0'
        })
        self.fields['vege_lunchbox'].widget.attrs.update({
            'max' : max_num*3,
            'min' : '0'
        })      


class EmailPostForm(forms.Form):
    email = forms.EmailField()


class SurveyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SurveyForm, self).__init__(*args, **kwargs)
        self.fields['os_for_ftime'].widget.attrs.update({
            'min' : '0'
        })
        self.fields['os_osc_ftime'].widget.attrs.update({
            'min' : '0'
        })
        self.fields['os_cn_ftime'].widget.attrs.update({
            'min' : '0'
        })
        self.fields['os_for_intern'].widget.attrs.update({
            'min' : '0'
        })
        self.fields['os_osc_intern'].widget.attrs.update({
            'min' : '0'
        })
        self.fields['os_cn_intern'].widget.attrs.update({
            'min' : '0'
        })
        self.fields['intern_week'].widget.attrs.update({
            'min' : '0'
        })
        self.fields['intern_hour'].widget.attrs.update({
            'min' : '0'
        })
        self.fields['intern_num'].widget.attrs.update({
            'min' : '0'
        })

    class Meta:
        model = rdss.models.CompanySurvey
        fields = '__all__'

    def save(self, commit=True):
        survey = super(SurveyForm, self).save(commit=False)
        if commit:
            survey.save()
        return survey


class StudentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.fields['idcard_no'].widget.attrs['autofocus'] = True

    class Meta:
        model = rdss.models.Student
        fields = ['idcard_no', 'student_id', 'phone', 'name', 'dep', 'email', 'other']

    def save(self, commit=True):
        form = super(StudentForm, self).save(commit=False)
        if commit:
            form.save()
        return form


class RedeemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RedeemForm, self).__init__(*args, **kwargs)

    class Meta:
        model = rdss.models.RedeemPrize
        fields = '__all__'
        exclude = ['updated', 'student']

    def save(self, commit=True):
        form = super(RedeemForm, self).save(commit=False)
        if commit:
            form.save()
        return form

class ImportStudentCardInfoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['excel_file'].label = u'檔案上傳'
    
    excel_file = forms.FileField()
