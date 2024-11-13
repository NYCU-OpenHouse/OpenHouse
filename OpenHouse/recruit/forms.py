from django import forms
from .models import (RecruitSignup,
                     JobfairInfo,
                     CompanySurvey,
                     SeminarInfo,
                     OnlineSeminarInfo,
                     Student,
                     ExchangePrize,
                     SeminarInfoTemporary,
                     JobfairInfoTemp)
from django.forms import ModelForm


class RecruitSignupForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(RecruitSignupForm, self).__init__(*args, **kwargs)
        self.fields['zone'].widget.attrs.update({
            'class': 'ui dropdown',
        })
        self.fields['history'].widget.attrs.update({
            'class': 'ui dropdown',
        })
        self.fields['seminar'].widget.attrs.update({
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
        model = RecruitSignup
        fields = '__all__'
        exclude = ['payment', 'receipt_no', 'ps']

    def save(self, commit=True):
        record = super(RecruitSignupForm, self).save(commit=False)
        if commit:
            record.save()
        return record


class SeminarInfoCreationForm(forms.ModelForm):
    class Meta:
        model = SeminarInfo
        fields = '__all__'
        exclude = ['cid']

    def __init__(self, *args, **kwargs):
        super(SeminarInfoCreationForm, self).__init__(*args, **kwargs)
        self.fields['contact_mobile'].widget.attrs.update({
            'placeholder': '格式：0912-345678',
        })

    def save(self, commit=True):
        record = super(SeminarInfoCreationForm, self).save(commit=False)
        if commit:
            record.save()
        return record


class OnlineSeminarInfoCreationForm(forms.ModelForm):
    class Meta:
        model = OnlineSeminarInfo
        fields = '__all__'
        exclude = ['cid']

    def __init__(self, *args, **kwargs):
        super(OnlineSeminarInfoCreationForm, self).__init__(*args, **kwargs)
        self.fields['contact_mobile'].widget.attrs.update({
            'placeholder': '格式：0912-345678',
        })

    def save(self, commit=True):
        record = super(OnlineSeminarInfoCreationForm, self).save(commit=False)
        if commit:
            record.save()
        return record


class SeminarInfoTemporaryCreationForm(forms.ModelForm):
    class Meta:
        model = SeminarInfoTemporary
        fields = '__all__'
        exclude = ['cid', 'live', 'order']
        help_texts = {
            'intro': '請勿使用網路特殊與表情符號，以免資訊無法送出'
        }

    def __init__(self, *args, **kwargs):
        super(SeminarInfoTemporaryCreationForm, self).__init__(*args, **kwargs)
        self.fields['contact_mobile'].widget.attrs.update({
            'placeholder': '格式：0912-345678',
        })

    def save(self, commit=True):
        record = super(SeminarInfoTemporaryCreationForm, self).save(commit=False)
        if commit:
            record.save()
        return record


class JobfairInfoForm(ModelForm):
    class Meta:
        model = JobfairInfo
        fields = '__all__'
        exclude = ['company']

    def __init__(self, *args, max_num=None, **kwargs):
        initial_data = kwargs.pop('initial', {})
        super(JobfairInfoForm, self).__init__(*args, **kwargs)

        # Set default values
        # (2025 recruit) The default value of total lunchbox is ${max_num * 3} meal_lunchbox.
        if not self.instance.pk or not self.instance.meat_lunchbox:
            default_meat_lunchbox = initial_data.get('meat_lunchbox', max_num*3)
            self.fields['meat_lunchbox'].initial = default_meat_lunchbox

        # Set attributes max and min
        self.fields['lunch_box'].widget.attrs.update({
            'max' : max_num*3,
            'min' : '0'
        })
        # (2025 recruit) For first booth, 2 tickets. For the rest, 1 ticket.
        parking_tickets_max = 2 + (max_num - 1) if max_num > 0 else 0
        self.fields['parking_tickets'].widget.attrs.update({
            'max' : parking_tickets_max,
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


class JobfairInfoTempForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['video'].label = u'影片 (請貼上 YouTube 影片網址)'

    class Meta:
        model = JobfairInfoTemp
        fields = '__all__'
        exclude = ['company']
        help_texts = {
            'content': '請勿使用網路特殊與表情符號，以免資訊無法送出'
        }


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
        model = CompanySurvey
        fields = '__all__'

    def save(self, commit=True):
        survey = super(SurveyForm, self).save(commit=False)
        if commit:
            survey.save()
        return survey


class StudentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.fields['card_num'].widget.attrs['autofocus'] = True

    class Meta:
        model = Student
        fields = ['card_num', 'student_id', 'phone', 'name', 'department', 'email']
    
    def save(self, commit=True):
        form = super(StudentForm, self).save(commit=False)
        if commit:
            form.save()
        return form


class ExchangeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExchangeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = ExchangePrize
        fields = '__all__'
        exclude = ['updated', 'student']

    def save(self, commit=True):
        form = super(ExchangeForm, self).save(commit=False)
        if commit:
            form.save()
        return form

class ImportStudentCardInfoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['excel_file'].label = u'檔案上傳'
    
    excel_file = forms.FileField()
