from django.shortcuts import redirect
from django.conf import settings
from djago.http import HttpResponseForbidden

class FailCloseMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # do the check from the permissions table here

        # then check the attribute on the view itself
        if getattr(view_func, 'safe'):
            return view_func(view_args, view_kwargs)

        if settings.FORBIDDEN_URL:
            return redirect(settings.FORBIDDEN_URL)
        else:
            return HttpResponseForbidden()


