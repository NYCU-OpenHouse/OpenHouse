from django.db import models
from django.contrib.admin.views.decorators import staff_member_required
from .models import Mentor, Signup
from django.http import HttpResponse
from django.utils.encoding import escape_uri_path
import xlsxwriter

@staff_member_required
def ExportStudentSignupStatus(request, id):
    if request.user and request.user.is_authenticated:
        if not request.user.is_superuser:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=403)

    mentor = Mentor.objects.get(id=id)
    filename =  "{}.xlsx".format(mentor.title)
    response = HttpResponse(content_type='application/ms-excel')  # microsoft excel
    # set "attachment" filename and allow chinese charater in filename
    response['Content-Disposition'] = 'attachment; filename=%s' % escape_uri_path(filename)
    workbook = xlsxwriter.Workbook(response)
    worksheet = workbook.add_worksheet("學生登記")
    # ignore id and cid which is index 0 and 1
    fields = list(Signup._meta.get_fields()[2:13])
    fields.append(Signup._meta.get_field('preferred_categories'))

    for index, field in enumerate(fields):
        worksheet.write(0, index, field.verbose_name)

    student_signup_status = mentor.signup_set.all()
    for row_count, info in enumerate(student_signup_status):
        for col_count, field in enumerate(fields):
            if field.name == 'preferred_categories':
                preferred_names = ", ".join([category.name for category in getattr(info, field.name).all()])
                worksheet.write(row_count + 1, col_count, preferred_names)
            elif isinstance(field, models.FileField):
                file_instance = getattr(info, field.name)
                if file_instance:
                    # file_url = file_instance.url
                    file_url = request.build_absolute_uri(file_instance.url)
                    worksheet.write(row_count + 1, col_count, file_url)
                else:
                    worksheet.write(row_count + 1, col_count, "")
            else:
                worksheet.write(row_count + 1, col_count, getattr(info, field.name))


    
    workbook.close()
    return response


