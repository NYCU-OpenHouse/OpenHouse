from django.db import models
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils import timezone



class CompanyVisit(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.CharField(u'廠商', max_length=30)
    title = models.CharField(u'標題', max_length=30)
    info = models.TextField(u'活動大綱', max_length=400, default='', blank=True)
    intro = models.TextField(u'行程介紹', max_length=400)
    departments = models.TextField(u'建議科系', max_length=400)
    event_more_info = RichTextUploadingField(u'活動更多資訊', default='', blank=True)
    mode = models.TextField(u'進行方式', max_length=400, default='', blank=True)
    remark = models.TextField(u'備註', max_length=400, default='', blank=True)
    signup_deadline = models.DateField(u'報名截止日期', default=timezone.now)
    date = models.DateField(u'參訪日期')
    start_time = models.TimeField(u'開始時間')
    end_time = models.TimeField(u'結束時間')
    place = models.CharField(u'參訪地點', max_length=30)
    name = models.CharField(u'聯絡人姓名', max_length=5)
    mobile = models.CharField(u'聯絡人手機', max_length=30)
    phone = models.CharField(u'聯絡人電話', max_length=30)
    email = models.EmailField(u'聯絡人email')
    limit = models.IntegerField(u'人數限制')

    def get_absolute_url(self):
        return reverse('company_visit_info', args=[self.id])

    def get_people_num(self):
        students = StudentApply.objects.filter(event=self)
        return sum([1 for student in students])

    class Meta:
        managed = True
        verbose_name = u'企業資訊'
        verbose_name_plural = u'企業資訊'

    def __str__(self):
        return self.title


class StudentApply(models.Model):
    GENDER = (
        (u'woman', u'女'),
        (u'man', u'男'),
        (u'other', u'其他'),
    )
    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(CompanyVisit, to_field='id', on_delete=models.CASCADE, verbose_name=u'場次/編號')
    name = models.CharField(u'姓名/護照姓名羅馬拼音(外國人使用)', max_length=10)
    student_id = models.CharField(u'學號', max_length=20)
    gender = models.CharField(u'性別', choices=GENDER, max_length=8)
    SSN = models.CharField(u'身分證字號/居留證字號/護照號碼', max_length=15)
    date = models.DateField(u'出生年月日')
    department = models.CharField(u'科系與年級', max_length=40)
    mobile = models.CharField(u'手機', max_length=15)
    email = models.EmailField(u'email')
    country = models.CharField(u'國籍', max_length=20, blank=True, null=True)

    class Meta:
        managed = True
        verbose_name = u'學生資訊'
        verbose_name_plural = u'學生資訊'
