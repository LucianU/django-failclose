from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

def safe(view):
    """Marks a view as safe to be called"""

    view.safe = True
    return view

def is_safe(view, rules=None):
    """Checks if a view has been marked as safe, and thus
    can be called"""

    if rules is None:
        if settings.PERMISSIONS_MODULE:
            rules = import_module(settings.PERMISSIONS_MODULE).RULES
        else:
            raise ImproperlyConfigured(
                    'You need to specify a PERMISSIONS_MODULE'
                    'in your settings.py'
            )

    # retrieving the view's app name and the corresponding safe_views list
    app_name = view.__module__.split('.')[-2]
    safe_views = rules.get(app_name)

    if safe_views is not None:
        # if the safe_views list is empty, it means that all views
        # are whitelisted
        if not safe_views or view.__name__ in safe_views:
            return True

    if getattr(view, 'safe', None):
        return True

    return False
