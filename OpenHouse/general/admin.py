from django.contrib import admin
from django.conf.urls import url,include
from general import models
import rdss.models

class NewsFileInline(admin.TabularInline):
    model = models.NewsFile
    fields = ['name', 'upload_file']
    readonly_fields = ('updated_time',)
    extra = 1

@admin.register(models.NewsFile)
class NewsFileAdmin(admin.ModelAdmin):
    list_display=('name', 'updated_time')

@admin.register(models.News)
class NewsAdmin(admin.ModelAdmin):
        list_display=('title','category','created_time','updated_time')
        inlines = [NewsFileInline]

@admin.register(models.PhotoSlide)
class PhotoSlideAdmin(admin.ModelAdmin):
        list_display=('title','order','photo', 'updated_time')

@admin.register(models.NavbarConfigs)
class NavbarConfigsAdmin(admin.ModelAdmin):
    list_display=['title']
    def title(self,obj):
        return '連結設定' # Register your models here.
