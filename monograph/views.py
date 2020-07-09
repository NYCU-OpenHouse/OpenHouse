from django.shortcuts import render
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import MonographInfo, Monograph


# Create your views here.
def index(request):
    """
    Function displaying latest intro and all monographs
    """
    try:
        mono_info = MonographInfo.objects.latest('updated')
    except MonographInfo.DoesNotExist:
        mono_info = None

    paginator = Paginator(Monograph.objects.all(), 16)
    page_number = request.GET.get('page')

    try:
        mono = paginator.page(page_number)
    except PageNotAnInteger:
        page_number = 1
        mono = paginator.page(page_number)
    except EmptyPage:
        page_number = paginator.num_pages
        mono = paginator.page(page_number)
    return render(request, 'monograph_index.html', locals())


def monograph_detail(request, monograph_id):
    """
    Function displaying specific monograph
    """
    try:
        mono = Monograph.objects.get(id=monograph_id)
    except Monograph.DoesNotExist:
        raise Http404('Monograph does not exist')

    previous = Monograph.objects.filter(updated__gt=mono.updated).last()
    next = Monograph.objects.filter(updated__lt=mono.updated).first()

    return render(request, 'monograph_detail.html', locals())
