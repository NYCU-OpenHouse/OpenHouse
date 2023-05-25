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

    paginator = Paginator(Monograph.objects.all(), 15)
    page_number = request.GET.get('page')
    carousel = Monograph.objects.all()[:10]

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
    
    mono.view_count += 1
    mono.save()
    
    recent_mono = Monograph.objects.all()[:5]
    
    hot_mono = Monograph.objects.order_by('-view_count', '-updated')[:5]
    
    if mono.priority:
        previous = Monograph.objects.filter(priority=True, updated__gt=mono.updated).last()
        next_mono = Monograph.objects.filter(priority=True, updated__lt=mono.updated).first()
        if not next_mono:
            next_mono = Monograph.objects.filter(priority=False).first()
    else:
        previous = Monograph.objects.filter(priority=False, updated__gt=mono.updated).last()
        next_mono = Monograph.objects.filter(priority=False, updated__lt=mono.updated).first()
        if not previous:
            previous = Monograph.objects.filter(priority=True).last()

    return render(request, 'monograph_detail.html', locals())
