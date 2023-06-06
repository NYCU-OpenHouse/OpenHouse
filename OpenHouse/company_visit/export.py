from django.contrib.admin.views.decorators import staff_member_required
from .models import CompanyVisit, StudentApply
from django.http import HttpResponse
from django.utils import timezone
from django.utils.encoding import escape_uri_path
import xlsxwriter

@staff_member_required
def ExportStudentSignupStatus(request, id):
    if request.user and request.user.is_authenticated:
        if not request.user.is_superuser:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=403)

    company_visit = CompanyVisit.objects.get(id=id)
    filename =  "{}_{}.xlsx".format(company_visit.title, timezone.localtime(timezone.now()).strftime("%Y%m%d-%H%M"))
    response = HttpResponse(content_type='application/ms-excel')  # microsoft excel
    # set "attachment" filename and allow chinese charater in filename
    response['Content-Disposition'] = 'attachment; filename=%s' % escape_uri_path(filename)
    workbook = xlsxwriter.Workbook(response)
    worksheet = workbook.add_worksheet("學生登記")
    # ignore id which is index 0
    fields = StudentApply._meta.get_fields()[2:11]
    for index, field in enumerate(fields):
        worksheet.write(0, index, field.verbose_name)

    student_signup_status = company_visit.studentapply_set.all()
    for row_count, info in enumerate(student_signup_status):
        for col_count, field in enumerate(fields):
            worksheet.write(row_count + 1, col_count, getattr(info, field.name))


    
    workbook.close()
    return response


