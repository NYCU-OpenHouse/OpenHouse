from django.db import models
from django.urls import reverse
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField


# Create your models here.
class Monograph(models.Model):
    """
    Model representing an monograph
    """
    id = models.AutoField(primary_key=True)
    title = models.CharField(u'標題', default='', max_length=20)
    cover = models.ImageField(u'封面', upload_to='monograph_images', null=True, blank=True,
                              help_text='僅接受 jpg, png, gif 格式。')
    content_1 = RichTextUploadingField(u'主內容', help_text='可以填入文字以及圖片')
    content_2 = RichTextField(u'附加內容', null=True, blank=True, help_text='只接受文字')
    image_1 = models.ImageField(u'圖片1', upload_to='monograph_images', null=True, blank=True,
                                help_text='僅接受 jpg, png, gif 格式。')
    image_2 = models.ImageField(u'圖片2', upload_to='monograph_images', null=True, blank=True,
                                help_text='僅接受 jpg, png, gif 格式。')
    priority = models.BooleanField(u'優先', default=False)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def get_absolute_url(self):
        """
        Function returning the absolute url of a monograph
        :return: url of the monograph
        """
        return reverse('monograph_detail', args=[str(self.id)])

    def __str__(self):
        """
        Function representing the object
        :return: String of the monograph's title
        """
        return self.title

    class Meta:
        ordering = ['-priority', '-updated']
        verbose_name = u'專刊'
        verbose_name_plural = u'專刊'


class MonographInfo(models.Model):
    """
    Model representing the introduction on monograph's main page
    """
    title = models.CharField(u'標題', default='', max_length=20)
    content = RichTextField(u'內容', null=True, blank=True)
    updated = models.DateTimeField(u'更新時間', auto_now=True)

    def __str__(self):
        """
        Function representing the object
        :return: String of the object
        """
        return "Monograph_Info"

    class Meta:
        verbose_name = u"專刊主頁資訊"
        verbose_name_plural = u"專刊主頁資訊"
