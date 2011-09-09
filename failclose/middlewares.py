from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpResponseForbidden

from failclose.utils import is_safe

class FailCloseMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # if the view is marked as safe, we execute it
        if is_safe(view_func):
            return view_func(request, *view_args, **view_kwargs)

        if settings.FORBIDDEN_URL:
            return redirect(settings.FORBIDDEN_URL)
        else:
            return HttpResponseForbidden()


