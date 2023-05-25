from django.contrib import admin
from . import models
from django import forms
from django.forms.widgets import HiddenInput


class CareerSeminarSignupInline(admin.TabularInline):
    model = models.Signup
    extra = 0
    exclude = ['time_available','question','cv_en','cv_zh','other']
    
class SignupInline(admin.TabularInline):
    model = models.Signup
    extra = 0
    
# Register your models here.
@admin.register(models.Mentor)
class CareerMentorAdmin(admin.ModelAdmin):
    # inlines = (SignupInline,)
    search_fields= ('company',)
    list_filter = ('category','company')
    list_display=('title','category', 'company', 'date','start_time','end_time',
                  'mentor', 'place','limit', 'updated' )
    def get_inline_instances(self, request, obj=None):
        inlines = []
        if obj:
            if obj.category == '職涯講座':
                inlines.append(CareerSeminarSignupInline)
            else:
                inlines.append(SignupInline)
        return [inline(self.model, self.admin_site) for inline in inlines]

@admin.register(models.Signup)
class CareerSignupAdmin(admin.ModelAdmin):
    date_hierarchy = 'mentor__date'
    list_filter = ('mentor','mentor__category')
    list_display=('mentor','dep', 'name', 'student_id','phone',
                  'email', 'time_available','question','cv_en','cv_zh','other', 'updated' )

