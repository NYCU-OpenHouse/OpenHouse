"""
Customized context for navbar
"""
from . import models

def nav_configs(request):
    return { 'nav_configs': models.NavbarConfigs.objects.last() }
