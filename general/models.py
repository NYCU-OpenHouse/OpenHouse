from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.


class News(models.Model):
    CATEGORYS = (
            (u'最新消息', u'最新消息'),
            (u'徵才專區', u'徵才專區')
            )
    PERM = (
            (u'index_only', u'只顯示於首頁'),
            (u'company_only', u'只顯示於廠商'),
            (u'both', u'顯示於首頁及廠商'),
            )
    id = models.AutoField(primary_key=True)
    title = models.CharField(u'標題', max_length=100)
    category = models.CharField(u'公告類別', max_length=5, choices=CATEGORYS)
    perm = models.CharField(u'誰能看到這則公告', max_length=15, choices=PERM)
    content = RichTextUploadingField(u'內容')
    created_time = models.DateTimeField(u'發佈時間', auto_now_add=True)
    updated_time = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        verbose_name = "公告系統"
        verbose_name_plural = "公告系統"


class NewsFile(models.Model):
    id = models.AutoField(primary_key=True)
    news_id = models.ForeignKey(News, to_field='id',
                        on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(u'檔名', max_length=50)
    upload_file = models.FileField(u'檔案',
                                    upload_to='news_files', null=True, blank=True)
    updated_time = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        verbose_name = "公告附件檔案"
        verbose_name_plural = "公告附件檔案"

class PhotoSlide(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(u'標題', max_length=50)
    order = models.IntegerField(u'順序')
    photo = models.ImageField(u"照片", upload_to='photo_slide',
                              help_text="照片請小於300K，過大的圖片會增加伺服器和使用者的負擔"
                              )
    updated_time = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        verbose_name = "首頁相片動畫"
        verbose_name_plural = "首頁相片動畫"

class NavbarConfigs(models.Model):
    show_jobfair = models.BooleanField(u'顯示校園徵才就博會連結')
    show_seminar = models.BooleanField(u'顯示校園徵才說明會連結')
    show_rdss_jobfair = models.BooleanField(u'顯示秋季徵才就博會連結')
    show_rdss_seminar = models.BooleanField(u'顯示秋季徵才說明會連結')

    class Meta:
        verbose_name = "公開頁面連結設定"
        verbose_name_plural = "公開頁面連結設定"
