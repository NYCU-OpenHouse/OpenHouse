from django.contrib import admin
from company.models import Company, ChineseFundedCompany, Job, CompanyCategories
from recruit import models as recruit_model
from careermentor.models import Mentor
from rdss import models as rdss_model
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.conf.urls import url, include
from . import export
from . import views


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
            # Update related models in recruit
            self.update_recruit(old_cid, new_cid)

            # Update related models in careermentor
            mentors = Mentor.objects.filter(cid=old_cid)
            if mentors.exists():
                for x in mentors:
                    x.cid = new_cid
                    x.save()

            # Update related models in rdss
            self.update_rdss(old_cid, new_cid)

        if commit:
            user.save()
        return user

    def update_recruit(self, old_cid, new_cid):
        """
        Update all related models in recruit
        """
        try:
            # Clone object with old cid and insert it back to table with new cid
            obj = recruit_model.RecruitSignup.objects.get(cid=old_cid)
            obj.pk = None
            obj.cid = new_cid
            obj.save()
            obj = recruit_model.RecruitSignup.objects.get(cid=new_cid)
        except Exception as e:
            obj = None
        if obj is not None:
            # Update all foreign keys of related models
            try:
                seminar_info = recruit_model.SeminarInfo.objects.get(company__cid=old_cid)
                seminar_info.company = obj
                seminar_info.save()
            except recruit_model.SeminarInfo.DoesNotExist:
                pass
            try:
                online_seminar_info = recruit_model.OnlineSeminarInfo.objects.get(company__cid=old_cid)
                online_seminar_info.company = obj
                online_seminar_info.save()
            except recruit_model.OnlineSeminarInfo.DoesNotExist:
                pass
            try:
                seminar_order = recruit_model.SeminarOrder.objects.get(company__cid=old_cid)
                seminar_order.company = obj
                seminar_order.save()
            except recruit_model.SeminarOrder.DoesNotExist:
                pass
            try:
                online_seminar_order = recruit_model.OnlineSeminarOrder.objects.get(company__cid=old_cid)
                online_seminar_order.company = obj
                online_seminar_order.save()
            except recruit_model.OnlineSeminarOrder.DoesNotExist:
                pass
            try:
                seminar_slot = recruit_model.SeminarSlot.objects.get(company__cid=old_cid)
                seminar_slot.company = obj
                seminar_slot.save()
            except recruit_model.SeminarSlot.DoesNotExist:
                pass
            try:
                online_seminar_slot = recruit_model.OnlineSeminarSlot.objects.get(company__cid=old_cid)
                online_seminar_slot.company = obj
                online_seminar_slot.save()
            except recruit_model.OnlineSeminarSlot.DoesNotExist:
                pass
            try:
                seminar_info_temp = recruit_model.SeminarInfoTemporary.objects.get(company__cid=old_cid)
                seminar_info_temp.company = obj
                seminar_info_temp.save()
            except recruit_model.SeminarInfoTemporary.DoesNotExist:
                pass
            try:
                jobfair_info = recruit_model.JobfairInfo.objects.get(company__cid=old_cid)
                jobfair_info.company = obj
                jobfair_info.save()
            except recruit_model.JobfairInfo.DoesNotExist:
                pass
            try:
                jobfair_info_temp = recruit_model.JobfairInfoTemp.objects.get(company__cid=old_cid)
                jobfair_info_temp.company = obj
                jobfair_info_temp.save()
            except recruit_model.JobfairInfoTemp.DoesNotExist:
                pass
            try:
                jobfair_order = recruit_model.JobfairOrder.objects.get(company__cid=old_cid)
                jobfair_order.company = obj
                jobfair_order.save()
            except recruit_model.JobfairOrder.DoesNotExist:
                pass
            jobfair_slot = recruit_model.JobfairSlot.objects.filter(company__cid=old_cid)
            if jobfair_slot.exists():
                for x in jobfair_slot:
                    x.company = obj
                    x.save()
            online_jobfair_slot = recruit_model.OnlineJobfairSlot.objects.filter(company__cid=old_cid)
            if online_jobfair_slot.exists():
                for x in online_jobfair_slot:
                    x.company = obj
                    x.save()
            sponsorship = recruit_model.SponsorShip.objects.filter(company__cid=old_cid)
            if sponsorship.exists():
                for x in sponsorship:
                    x.company = obj
                    x.save()
            # Update cid of other models
            try:
                survey = recruit_model.CompanySurvey.objects.get(cid=old_cid)
                survey.cid = new_cid
                survey.save()
            except recruit_model.CompanySurvey.DoesNotExist:
                pass
            # Remove object with old cid from table
            recruit_model.RecruitSignup.objects.get(cid=old_cid).delete()

    def update_rdss(self, old_cid, new_cid):
        """
        Update all related models in rdss
        """
        try:
            # Clone object with old cid and insert it back to table with new cid
            obj = rdss_model.Signup.objects.get(cid=old_cid)
            obj.pk = None
            obj.cid = new_cid
            obj.save()
            obj = rdss_model.Signup.objects.get(cid=new_cid)
        except Exception as e:
            obj = None
        if obj is not None:
            # Update all foreign keys of related models
            try:
                seminar_info = rdss_model.SeminarInfo.objects.get(company__cid=old_cid)
                seminar_info.company = obj
                seminar_info.save()
            except rdss_model.SeminarInfo.DoesNotExist:
                pass
            try:
                seminar_order = rdss_model.SeminarOrder.objects.get(company__cid=old_cid)
                seminar_order.company = obj
                seminar_order.save()
            except rdss_model.SeminarOrder.DoesNotExist:
                pass
            try:
                seminar_slot = rdss_model.SeminarSlot.objects.get(company__cid=old_cid)
                seminar_slot.company = obj
                seminar_slot.save()
            except rdss_model.SeminarSlot.DoesNotExist:
                pass
            try:
                jobfair_info = rdss_model.JobfairInfo.objects.get(company__cid=old_cid)
                jobfair_info.company = obj
                jobfair_info.save()
            except rdss_model.JobfairInfo.DoesNotExist:
                pass
            try:
                jobfair_order = rdss_model.JobfairOrder.objects.get(company__cid=old_cid)
                jobfair_order.company = obj
                jobfair_order.save()
            except rdss_model.JobfairOrder.DoesNotExist:
                pass
            jobfair_slot = rdss_model.JobfairSlot.objects.filter(company__cid=old_cid)
            if jobfair_slot.exists():
                for x in jobfair_slot:
                    x.company = obj
                    x.save()
            online_jobfair_slot = rdss_model.OnlineJobfairSlot.objects.filter(company__cid=old_cid)
            if online_jobfair_slot.exists():
                for x in online_jobfair_slot:
                    x.company = obj
                    x.save()
            sponsorship = rdss_model.Sponsorship.objects.filter(company__cid=old_cid)
            if sponsorship.exists():
                for x in sponsorship:
                    x.company = obj
                    x.save()
            # Update cid of other models
            try:
                survey = rdss_model.CompanySurvey.objects.get(cid=old_cid)
                survey.cid = new_cid
                survey.save()
            except rdss_model.CompanySurvey.DoesNotExist:
                pass
            # Remove object with old cid from table
            rdss_model.Signup.objects.get(cid=old_cid).delete()

'''
List all companies not in the category list
'''
class InvalidCategoryFilter(admin.SimpleListFilter):
    title = '非法類別'
    parameter_name = 'invalid_category_filter'

    def lookups(self, request, model_admin):
        categories = CompanyCategories.objects.all()
        companies_distinct_categories_ids = Company.objects.values_list('categories', flat=True).distinct()
        companies_distinct_categories = [CompanyCategories.objects.get(id=id) for id in companies_distinct_categories_ids]
        invalid_categories = set(companies_distinct_categories) - set(categories)
        return [(category, category) for category in invalid_categories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category=self.value())
        return queryset

class JobInline(admin.StackedInline):
    model = Job
    fields = ('title', 'quantity', 'is_liberal', 'is_foreign', 'description', 'note', 'english_title', 'english_description', 'english_note')
    extra = 0

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('cid', 'name', 'categories', 'hr_name', 'hr_phone', 'hr_email', 'chinese_funded', 'jobs_summary', 'last_update', 'date_join')
    list_filter = (InvalidCategoryFilter, 'chinese_funded', 'categories',)
    fieldsets = (
        ("基本資料", {
            'classes': ('wide',),
            'fields': ('cid', 'password', 'name', 'english_name', 'shortname', 'categories', 'phone',
                       'postal_code', 'address', 'website', 'brief', 'recruit_info', 'logo', 'recruit_url',
                       'business_project', 'relation_business', 'subsidiary')
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
        ("其他備註資料", {
            'classes': ('wide',),
            'fields': ('payment_ps', 'other_ps')
        }
         ),
         ("會員身份", {
            'classes': ('wide',),
            'fields': ('ece_member_normal', 'ece_member', 'gloria_normal', 'gloria_startup')
        }
         ),
         ("收據資訊", {
            'classes': ('wide',),
            'fields': ('receipt_title', 'receipt_code', 'receipt_postal_code', 'receipt_postal_address',
                       'receipt_contact_name', 'receipt_contact_email', 'receipt_contact_phone')
        }
         ),
         ("中資", {
            'classes': ('wide',),
            'fields': ('chinese_funded',)
        }
         ),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        ("基本資料", {
            'classes': ('wide',),
            'fields': ('cid', 'password1', 'password2', 'name', 'english_name', 'shortname',
                       'categories', 'phone', 'postal_code', 'address', 'website', 'brief', 'recruit_info', 'logo',
                       'recruit_url', 'business_project', 'relation_business', 'subsidiary')
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
        ("其他備註資料", {
            'classes': ('wide',),
            'fields': ('payment_ps', 'other_ps')
        }
         ),
         ("會員身份", {
            'classes': ('wide',),
            'fields': ('ece_member_normal', 'ece_member', 'gloria_normal', 'gloria_startup')
        }
         ),
         ("收據資訊", {
            'classes': ('wide',),
            'fields': ('receipt_title', 'receipt_code', 'receipt_postal_code', 'receipt_postal_address',
                       'receipt_contact_name', 'receipt_contact_email', 'receipt_contact_phone')
        }
         ),
         ("中資", {
            'classes': ('wide',),
            'fields': ('chinese_funded',)
        }
         ),
    )
    search_fields = ('cid', 'name', 'english_name', 'shortname')
    ordering = ('cid',)
    filter_horizontal = ()
    inlines = [JobInline]

    # upadet category action
    categories = CompanyCategories.objects.all()
    actions = [f'update_to_{category.name}' for category in categories]
    def generate_update_action(self, new_category):
        def update_category(self, request, queryset):
            for company in queryset:
                company.categories = new_category
                company.save()
        return update_category

    for category in categories:
        action_name = f'update_to_{category.name}'
        action_func = generate_update_action(None, category)
        setattr(UserAdmin, action_name, action_func)
        setattr(getattr(UserAdmin, action_name), 'short_description', f"變更類別至 '{category.name}'")

    # (for 2024 rdss) migrate category to categories action
    def migrate_category_to_categories(self, request, queryset):
        for company in queryset:
            try:
                category_obj = CompanyCategories.objects.get(name=company.category)
            except CompanyCategories.DoesNotExist:
                category_obj = CompanyCategories.objects.get(name='其他')
            company.categories = category_obj
            company.save()
    
    actions.append('migrate_category_to_categories')

    def get_urls(self):
        urls = super(UserAdmin, self).get_urls()
        my_urls = [
            url(r'^export/$', export.Export_Company),
            url(r'^registered_chinese_funded_company/$',views.regitered_chinese_funded_company),  
        ]
        return my_urls + urls
    
    def total_jobs(self, obj):
        return obj.company_job_set.count()

    def liberal_jobs(self, obj):
        return obj.company_job_set.filter(is_liberal=True).count()

    def foreign_jobs(self, obj):
        return obj.company_job_set.filter(is_foreign=True).count()
    
    def jobs_summary(self, obj):
        total = self.total_jobs(obj)
        liberal = self.liberal_jobs(obj)
        foreign = self.foreign_jobs(obj)
        return f'職缺數: {total}, 文組職缺: {liberal}, 外籍職缺: {foreign}'
    
    jobs_summary.short_description = '職缺概覽'

# Now register the new UserAdmin...
admin.site.register(Company, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
# admin.site.unregister(Group)

@admin.register(ChineseFundedCompany)
class ChineseFundedCompanyAdmin(admin.ModelAdmin):
    search_fields = ('cid', 'name')
    list_display = ('cid', 'name','updated_time')

@admin.register(CompanyCategories)
class CompanyCategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'discount')
