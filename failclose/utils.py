from failclose.permissions import RULES

def safe(view):
    view.safe = True
    return view

def is_safe(view):
    # retrieving the view's app name and the corresponding views list
    app_name = view.__module__.split('.')[-2]
    views = RULES.get(app_name)

    if views is not None:
        # if the views list is empty, it means that all views
        # are whitelisted
        if not views or view.__name__ in views:
            return True

    if getattr(view, 'safe', None) is None:
        return False

