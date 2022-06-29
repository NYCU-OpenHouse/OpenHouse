from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django import forms
from company.models import Company
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.translation import ugettext as _


class CompanyCreationForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': ('兩次輸入的密碼不一樣'),
        'cid_error': ('統一編號必需都是數字'),
    }
    # customed fields
    cid = forms.CharField(label=(u'公司統一編號'), help_text='請輸入8位數統一編號')
    password1 = forms.CharField(label=(u'密碼'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=(u'密碼確認'),
                                widget=forms.PasswordInput, help_text=('請再次輸入密碼'))

    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super(CompanyCreationForm, self).__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({
            'class': 'ui dropdown',
        })

    class Meta:
        model = Company
        fields = '__all__'
        exclude = ['id', 'password', 'last_login', 'is_active']
        widgets = {
            'brief': forms.Textarea(attrs={'cols': 80, 'rows': 8}),
            'recruit_info': forms.Textarea(attrs={'cols': 80, 'rows': 8}),
            'recruit_url': forms.Textarea(attrs={'cols': 80, 'rows': 8}),
        }

    class Media:
        js = ('js/company/company_create_form.js',)
        css = {
            'all': ('css/company/company_create_form.css',),
        }

    def clean_cid(self):
        cid = self.cleaned_data.get('cid')
        if not cid.isdigit():
            raise forms.ValidationError(
                self.error_messages['cid_error'],
                code='cid_error'
            )
        return cid

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch'
            )
        return password2

    def save(self, commit=True):
        user = super(CompanyCreationForm, self).save(commit=False)
        user.last_login = timezone.now()
        user.set_password(self.cleaned_data['password2'])
        if commit:
            user.save()
        return user


class CompanyEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CompanyEditForm, self).__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({
            'class': 'ui disabled dropdown',
        })
        self.fields['cid'].widget.attrs['readonly'] = True

        required_css_class = 'required'

    class Meta:
        model = Company
        fields = '__all__'
        exclude = ['password', 'last_login', 'date_join', 'is_active']
        widgets = {
            'brief': forms.Textarea(),
            'recruit_info': forms.Textarea(),
            'recruit_url': forms.Textarea(),
        }

    # css/js for the form, need to put {{form.media}} in template
    class Media:
        js = ('js/company/company_edit_form.js',)
        css = {
            'all': ('css/company/company_edit_form.css',),
        }

    # ref here https://docs.djangoproject.com/en/1.8/ref/forms/validation/  search clean_
    def save(self, commit=True):
        user = super(CompanyEditForm, self).save(commit=False)
        if commit:
            user.save()
        return user


class CompanyPasswordResetForm(PasswordResetForm):
    error_messages = {
        'does_not_exist': _("這個帳號不存在"),
    }
    user = forms.CharField(max_length=8)
    to_email = None

    def save(self, request=None):
        current_site = get_current_site(request)
        company = Company.objects.get(cid=self.cleaned_data['user'])
        to_email = company.hr_email
        context = {
            'email': to_email,
            'domain': current_site.domain,
            'site_name': current_site.name,
            'uid': urlsafe_base64_encode(force_bytes(company.pk)),
            'user': company,
            'token': default_token_generator.make_token(company),
            'protocol': 'https',
            'company_name': company.shortname
        }
        subject_template = "password_reset_subject.txt"
        email_body_template = 'password_reset_email.html'
        from_email = "交通大學 OpenHouse <password_reset@openhouse.nctu.edu.tw>"
        self.send_mail(subject_template, email_body_template, context, from_email, to_email)

    def clean_user(self):
        user = self.cleaned_data.get('user')
        try:
            Company.objects.get(cid=user)
        except:
            raise forms.ValidationError(
                self.error_messages['does_not_exist'],
                code='does_not_exist')
        return user
