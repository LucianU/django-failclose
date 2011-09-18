from django.conf.urls.defaults import patterns
from django.template import RequestContext, Template
from django.views.decorators.cache import never_cache
from django.http import HttpResponse

from failclose.utils import safe

@never_cache
@safe
def pretty(request):
    t = Template("Salutations from the pretty view!")
    return HttpResponse(t.render(RequestContext(request)))

@never_cache
def ugly(request):
    t = Template("Ugly view says 'Hi' too.")
    return HttpResponse(t.render(RequestContext(request)))

urlpatterns = patterns('',
    (r'^pretty/$', pretty),
    (r'^ugly/$', ugly),
)
