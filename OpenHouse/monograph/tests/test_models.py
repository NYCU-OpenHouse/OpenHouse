from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from monograph.models import MonographInfo, Monograph
import os


# Create your tests here.
class MonographIntroTest(TestCase):
    """
    Class testing model of MonographIntro
    There are 7 tests
    """

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        MonographInfo.objects.create(title='MonographIntroTest')

    # Title
    def test_title_name_label(self):
        mono = MonographInfo.objects.get(title='MonographIntroTest')
        label = mono._meta.get_field('title').verbose_name
        self.assertEqual(label, u'標題')

    def test_title_max_length(self):
        mono = MonographInfo.objects.get(title='MonographIntroTest')
        length = mono._meta.get_field('title').max_length
        self.assertEqual(length, 20)

    # Content
    def test_content_name_label(self):
        mono = MonographInfo.objects.get(title='MonographIntroTest')
        label = mono._meta.get_field('content').verbose_name
        self.assertEqual(label, u'內容')

    def test_content_null_and_blank(self):
        mono = MonographInfo.objects.get(title='MonographIntroTest')
        null = mono._meta.get_field('content').null
        blank = mono._meta.get_field('content').blank
        self.assertTrue(null)
        self.assertTrue(blank)

    # Updated
    def test_updated_name_label(self):
        mono = MonographInfo.objects.get(title='MonographIntroTest')
        label = mono._meta.get_field('updated').verbose_name
        self.assertEqual(label, u'更新時間')

    def test_updated_auto_now(self):
        mono = MonographInfo.objects.get(title='MonographIntroTest')
        auto = mono._meta.get_field('updated').auto_now
        self.assertTrue(auto)

    # Object
    def test_object_name(self):
        mono = MonographInfo.objects.get(title='MonographIntroTest')
        self.assertEqual(str(mono), 'Monograph_Info')


class MonographTest(TestCase):
    """
    Class testing model of Monograph
    There are 22 tests
    """

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        Monograph.objects.create(title='MonographTest',
                                 content_1='This is a test',
                                 image_1=SimpleUploadedFile(name='test_logo.jpg',
                                                            content=open(base_dir + '/tests/test_logo.jpg',
                                                                         'rb').read(),
                                                            content_type='image/jpeg'))

    # Title
    def test_title_name_label(self):
        mono = Monograph.objects.get(title='MonographTest')
        label = mono._meta.get_field('title').verbose_name
        self.assertEqual(label, u'標題')

    def test_title_max_length(self):
        mono = Monograph.objects.get(title='MonographTest')
        length = mono._meta.get_field('title').max_length
        self.assertEqual(length, 20)

    # Cover
    def test_cover_name_label(self):
        mono = Monograph.objects.get(title='MonographTest')
        label = mono._meta.get_field('cover').verbose_name
        self.assertEqual(label, u'封面')

    def test_cover_help_text(self):
        mono = Monograph.objects.get(title='MonographTest')
        help_text = mono._meta.get_field('cover').help_text
        self.assertEqual(help_text, '僅接受 jpg, png, gif 格式。')

    def test_cover_null_and_blank(self):
        mono = Monograph.objects.get(title='MonographTest')
        null = mono._meta.get_field('cover').null
        blank = mono._meta.get_field('cover').blank
        self.assertTrue(null)
        self.assertTrue(blank)

    # Content 1
    def test_content_1_name_label(self):
        mono = Monograph.objects.get(title='MonographTest')
        label = mono._meta.get_field('content_1').verbose_name
        self.assertEqual(label, u'主內容')

    def test_content_1_help_text(self):
        mono = Monograph.objects.get(title='MonographTest')
        help = mono._meta.get_field('content_1').help_text
        self.assertEqual(help, '可以填入文字以及圖片')

    # Content 2
    def test_content_2_name_label(self):
        mono = Monograph.objects.get(title='MonographTest')
        label = mono._meta.get_field('content_2').verbose_name
        self.assertEqual(label, u'附加內容')

    def test_content_2_help_text(self):
        mono = Monograph.objects.get(title='MonographTest')
        help_text = mono._meta.get_field('content_2').help_text
        self.assertEqual(help_text, '只接受文字')

    def test_content_2_null_and_blank(self):
        mono = Monograph.objects.get(title='MonographTest')
        null = mono._meta.get_field('content_2').null
        blank = mono._meta.get_field('content_2').blank
        self.assertTrue(null)
        self.assertTrue(blank)

    # Image 1
    def test_image_1_name_label(self):
        mono = Monograph.objects.get(title='MonographTest')
        label = mono._meta.get_field('image_1').verbose_name
        self.assertEqual(label, u'圖片1')

    def test_image_1_help_text(self):
        mono = Monograph.objects.get(title='MonographTest')
        help_text = mono._meta.get_field('image_1').help_text
        self.assertEqual(help_text, '僅接受 jpg, png, gif 格式。')

    def test_image_1_null_and_blank(self):
        mono = Monograph.objects.get(title='MonographTest')
        null = mono._meta.get_field('image_1').null
        blank = mono._meta.get_field('image_1').blank
        self.assertTrue(null)
        self.assertTrue(blank)

    # Image 2
    def test_image_2_name_label(self):
        mono = Monograph.objects.get(title='MonographTest')
        label = mono._meta.get_field('image_2').verbose_name
        self.assertEqual(label, u'圖片2')

    def test_image_2_help_text(self):
        mono = Monograph.objects.get(title='MonographTest')
        help_text = mono._meta.get_field('image_2').help_text
        self.assertEqual(help_text, '僅接受 jpg, png, gif 格式。')

    def test_image_2_null_and_blank(self):
        mono = Monograph.objects.get(title='MonographTest')
        null = mono._meta.get_field('image_2').null
        blank = mono._meta.get_field('image_2').blank
        self.assertTrue(null)
        self.assertTrue(blank)

    # Priority
    def test_priority_name_label(self):
        mono = Monograph.objects.get(title='MonographTest')
        label = mono._meta.get_field('priority').verbose_name
        self.assertEqual(label, u'優先')

    def test_priority_default(self):
        mono = Monograph.objects.get(title='MonographTest')
        default = mono._meta.get_field('priority').default
        self.assertFalse(default)

    # Updated
    def test_updated_name_label(self):
        mono = Monograph.objects.get(title='MonographTest')
        label = mono._meta.get_field('updated').verbose_name
        self.assertEqual(label, u'更新時間')

    def test_updated_auto_now(self):
        mono = Monograph.objects.get(title='MonographTest')
        auto = mono._meta.get_field('updated').auto_now
        self.assertTrue(auto)

    # Object
    def test_object_name(self):
        mono = Monograph.objects.get(title='MonographTest')
        self.assertEqual(str(mono), 'MonographTest')

    def test_get_absolute_url(self):
        mono = Monograph.objects.get(title='MonographTest')
        self.assertEqual(mono.get_absolute_url(), '/monograph/{}/'.format(mono.id))
