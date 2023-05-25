from django.contrib import admin
from . import models


# Register your models here.
@admin.register(models.Monograph)
class MonographAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'priority','view_count', 'updated',)
    readonly_fields = ['view_count',]


@admin.register(models.MonographInfo)
class MonographInfoAdmin(admin.ModelAdmin):
    list_display = ('title', 'updated',)
