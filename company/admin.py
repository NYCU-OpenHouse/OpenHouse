from django.contrib import admin
from company.models import Company
from recruit.models import RecruitSignup, SeminarInfo, SeminarOrder, SeminarSlot, SeminarInfoTemporary, JobfairInfo, \
    JobfairInfoTemp, JobfairOrder, JobfairSlot, SponsorShip
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.conf.urls import url, include
from . import export


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = Company
        fields = '__all__'

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(label=("Password"),
                                         help_text=("<h3><a href=\"../password/\">變更廠商密碼</a></h3>"))

    class Meta:
        model = Company
        fields = ['name']

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

    def save(self, commit=True):
        user = super(UserChangeForm, self).save(commit=False)
        old_cid = self.initial['cid']
        new_cid = self.data['cid']
        if old_cid != new_cid:
            # RecruitSignup.objects.filter(cid=old_cid).update(cid=new_cid)
            try:
                # Clone object with old cid and insert it back to table with new cid
                obj = RecruitSignup.objects.get(cid=old_cid)
                obj.pk = None
                obj.cid = new_cid
                obj.save()
                obj = RecruitSignup.objects.get(cid=new_cid)
            except Exception as e:
                obj = None

            if obj is not None:
                # Update all foreign keys of related models
                try:
                    seminar_info = SeminarInfo.objects.get(company__cid=old_cid)
                    seminar_info.company = obj
                    seminar_info.save()
                except SeminarInfo.DoesNotExist:
                    pass
                try:
                    seminar_order = SeminarOrder.objects.get(company__cid=old_cid)
                    seminar_order.company = obj
                    seminar_order.save()
                except SeminarOrder.DoesNotExist:
                    pass
                try:
                    seminar_slot = SeminarSlot.objects.get(company__cid=old_cid)
                    seminar_slot.company = obj
                    seminar_slot.save()
                except SeminarSlot.DoesNotExist:
                    pass
                try:
                    seminar_info_temp = SeminarInfoTemporary.objects.get(company__cid=old_cid)
                    seminar_info_temp.company = obj
                    seminar_info_temp.save()
                except SeminarInfoTemporary.DoesNotExist:
                    pass
                try:
                    jobfair_info = JobfairInfo.objects.get(company__cid=old_cid)
                    jobfair_info.company = obj
                    jobfair_info.save()
                except JobfairInfo.DoesNotExist:
                    pass
                try:
                    jobfair_info_temp = JobfairInfoTemp.objects.get(company__cid=old_cid)
                    jobfair_info_temp.company = obj
                    jobfair_info_temp.save()
                except JobfairInfoTemp.DoesNotExist:
                    pass
                try:
                    jobfair_order = JobfairOrder.objects.get(company__cid=old_cid)
                    jobfair_order.company = obj
                    jobfair_order.save()
                except JobfairOrder.DoesNotExist:
                    pass
                jobfair_slot = JobfairSlot.objects.filter(company__cid=old_cid)
                if jobfair_slot.exists():
                    for x in jobfair_slot:
                        x.company = obj
                        x.save()
                sponsorship = SponsorShip.objects.filter(company__cid=old_cid)
                if sponsorship.exists():
                    for x in sponsorship:
                        x.company = obj
                        x.save()
            # Remove object with old cid from table
            RecruitSignup.objects.get(cid=old_cid).delete()

        if commit:
            user.save()
        return user


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('cid', 'name', 'category', 'hr_name', 'hr_phone', 'hr_email', 'last_update')
    list_filter = ()
    fieldsets = (
        ("基本資料", {
            'classes': ('wide',),
            'fields': ('cid', 'password', 'name', 'shortname', 'category', 'phone',
                       'postal_code', 'address', 'website', 'brief', 'recruit_info', 'logo', 'recruit_url',
                       'business_project', 'relation_business', 'subsidiary', 'receipt_title')
        }
         ),
        ("人資資料", {
            'classes': ('wide',),
            'fields': ('hr_name', 'hr_phone', 'hr_fax', 'hr_mobile', 'hr_email')
        }
         ),
        ("第二位人資資料", {
            'classes': ('wide',),
            'fields': ('hr2_name', 'hr2_phone', 'hr2_fax', 'hr2_mobile', 'hr2_email', 'hr_ps')
        }
         ),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        ("基本資料", {
            'classes': ('wide',),
            'fields': ('cid', 'password1', 'password2', 'name', 'shortname',
                       'category', 'phone', 'postal_code', 'address', 'website', 'brief', 'recruit_info', 'logo',
                       'recruit_url', 'receipt_title')
        }
         ),
        ("人資資料", {
            'classes': ('wide',),
            'fields': ('hr_name', 'hr_phone', 'hr_fax', 'hr_mobile', 'hr_email')
        }
         ),
        ("第二位人資資料", {
            'classes': ('wide',),
            'fields': ('hr2_name', 'hr2_phone', 'hr2_fax', 'hr2_mobile', 'hr2_email', 'hr_ps')
        }
         ),
    )
    search_fields = ('cid', 'name', 'shortname')
    ordering = ('cid',)
    filter_horizontal = ()

    def get_urls(self):
        urls = super(UserAdmin, self).get_urls()
        my_urls = [
            url(r'^export/$', export.Export_Company),
        ]
        return my_urls + urls


# Now register the new UserAdmin...
admin.site.register(Company, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
# admin.site.unregister(Group)
