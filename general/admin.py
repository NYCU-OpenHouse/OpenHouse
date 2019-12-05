from django.contrib import admin
from django.conf.urls import url,include
from general import models
import rdss.models

@admin.register(models.News)
class NewsAdmin(admin.ModelAdmin):
	list_display=('title','category','created_time','updated_time')

@admin.register(models.PhotoSlide)
class PhotoSlideAdmin(admin.ModelAdmin):
	list_display=('title','order','photo', 'updated_time')

@admin.register(models.NavbarConfigs)
class NavbarConfigsAdmin(admin.ModelAdmin):
    list_display=['title']
    def title(self,obj):
        return '連結設定'
# Register your models here.
