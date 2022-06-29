from django.shortcuts import render,get_object_or_404
from .models import CompanyVisit
from .forms import StudentApplyForm
from datetime import datetime
def company_visit_index(request):
    events = CompanyVisit.objects.all().order_by('date')
    events = [event for event in events if event.date > datetime.today().date()]

    return render(request, "visit/company_visit_index.html", locals())

def company_visit_info(request,id):
    event = get_object_or_404(CompanyVisit, id=id)
    return render(request, "visit/visit_info.html", locals())

def company_visit_apply(request,id):
    event = get_object_or_404(CompanyVisit,id=id)
    init_data={'event': event}
    form = StudentApplyForm(initial=init_data)
    if event.get_people_num() >= event.limit:
        message = True
    if(request.method=='POST'):
        data = request.POST.copy()
        form = StudentApplyForm(data)
        if form.is_valid():
            form.save()
            return render(request,'visit/company_visit_success.html',locals())
    return render(request, "visit/company_visit_apply.html", locals())
