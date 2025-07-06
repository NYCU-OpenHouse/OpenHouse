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
    pinned = models.BooleanField(u'置頂貼文', default=False)
    category = models.CharField(u'公告類別', max_length=5, choices=CATEGORYS)
    perm = models.CharField(u'誰能看到這則公告', max_length=15, choices=PERM)
    expiration_time = models.DateField(u'下架日期', null=True, blank=True, help_text="公告的截止日期，當天過期後不顯示於首頁")
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
    id = models.AutoField(primary_key=True)
    show_recruit = models.BooleanField(u'顯示校園徵才', default=False)
    show_jobfair = models.BooleanField(u'顯示校園徵才實體就博會連結', default=False)
    show_recruit_online_jobfair = models.BooleanField(u'顯示校園徵才線上就博會連結', default=False)
    show_seminar = models.BooleanField(u'顯示校園徵才實體說明會連結', default=False)
    show_recruit_ece_seminar = models.BooleanField(u'顯示校園徵才實體ECE說明會連結', default=False)
    show_recruit_online_seminar = models.BooleanField(u'顯示校園徵才線上說明會連結', default=False)
    
    show_rdss = models.BooleanField(u'顯示秋季招募', default=False)
    show_rdss_jobfair = models.BooleanField(u'顯示秋季徵才就博會連結')
    show_rdss_online_jobfair = models.BooleanField(u'顯示秋季徵才線上就博會連結', default=False)
    show_rdss_seminar = models.BooleanField(u'顯示秋季徵才說明會連結')

    class Meta:
        verbose_name = "公開頁面連結設定"
        verbose_name_plural = "公開頁面連結設定"

class FAQ_new(models.Model):
    id = models.AutoField(primary_key=True)
    content = RichTextUploadingField(u'內容')
    
    class Meta:
        verbose_name = "常見問題"
        verbose_name_plural = "常見問題"

class HistoryImg(models.Model):
    id = models.AutoField(primary_key=True)
    upload_img = models.ImageField(u'上傳檔案',
                                   upload_to='history_files', null=False)
    order = models.IntegerField(u'順序')
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    class Meta:
        verbose_name = u"歷史沿革圖片上傳"
        verbose_name_plural = u"歷史沿革圖片上傳"

class Member(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    title = models.CharField(max_length=20)
    start_term = models.PositiveIntegerField(
        verbose_name="起始屆",
        help_text="起始屆數從1988年秋季開始算起，第一屆為1988年秋季-1989年春季"
    )
    end_term = models.PositiveIntegerField(
        verbose_name="結束屆",
        help_text="若此幹部只任職一屆，起始屆和結束屆數相同(38-38)；若任職多屆，則起始屆小於結束屆(35-38)"
    )
    message = models.TextField(blank=True)

    class Meta:
        verbose_name = u"各屆幹部"
        verbose_name_plural = u"各屆幹部"

    def __str__(self):
        if self.start_term == self.end_term:
            return f"第{self.start_term}屆 {self.title} {self.name}"
        return f"第{self.start_term}~{self.end_term}屆 {self.title} {self.name}"

    def get_all_terms(self):
        """回傳這個幹部所任職的所有屆數（list）"""
        return list(range(self.start_term, self.end_term + 1))

    def get_term_range_str(self):
        start_year = 1988 + (self.start_term - 1)
        end_year = 1988 + self.end_term
        return f"{start_year} 秋季 - {end_year} 春季"
