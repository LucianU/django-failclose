from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.db.models.loading import get_app

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
                    'You need to specify a PERMISSIONS_MODULE '
                    'in your settings.py'
            )

    _validate_rules(rules)

    # retrieving the view's app name and the corresponding safe_views list
    app_name = _get_app_name(view)
    safe_views = rules.get(app_name)

    if safe_views is not None:
        # if the safe_views list is empty, it means that all views
        # are whitelisted
        if not safe_views or view.__name__ in safe_views:
            return True

    if getattr(view, 'safe', None):
        return True

    return False

def _get_app_name(view):
    path_components = view.__module__.split('.')
    project_name = _get_project_name()

    for comp in path_components:
        try:
            get_app(comp, emptyOK=True)
        except ImproperlyConfigured:
            pass
        else:
            return comp

    if project_name in path_components:
        return project_name

    raise ImproperlyConfigured(
            "Couldn't find the app the view %s belongs to."
            "The view's import path is %s" % (view, view.__module__)
    )

def _get_project_name():
    PROJECT_NAME = getattr(settings, 'PROJECT_NAME', None)

    if PROJECT_NAME:
        return PROJECT_NAME
    else:
        parts = settings.ROOT_URLCONF.split('.')
        if len(parts) != 2:
            raise ImproperlyConfigured(
                    "You've changed the structure of ROOT_URLCONF, "
                    "so you need to set PROJECT_NAME in your settings.py"
            )
        return parts[0]

def _validate_rules(rules):
    project_name = _get_project_name()

    for app in rules.iterkeys():
        try:
            get_app(app, emptyOK=True)
        except ImproperlyConfigured:
            if app != project_name:
                raise
