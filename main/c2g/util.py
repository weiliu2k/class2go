import settings
import urlparse

from django.contrib.sites.models import Site
from django.core.files.storage import FileSystemStorage, get_storage_class
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.functional import wraps


def is_storage_local():
    """Check whether django believes it's keeping things on local disk"""
    return get_storage_class() == FileSystemStorage

def get_site_domain():
    """Return a bare domain name for the current site"""
    return Site.objects.get_current().domain

def get_site_url():
    """Return a fully qualified URL for the current site"""
    # FIXME: assumes http, but we should be able to tell
    site = Site.objects.get_current()
    url = 'http://%s/' % (site.domain)
    return url

def get_host_no_port(request):
    hn = request.get_host()
    if request.get_host().endswith(":443"):
        hn = hn[:-4]

    if request.get_host().endswith(":80"):
        hn = hn[:-3]

    return hn


def redirects_use_http(response, request):
    '''This function changes all REDIRECT responses to http if they are https.
        Useful for downgrades after login/reg, etc.
    '''
    hn = request.get_host()
    if (settings.INSTANCE == 'stage' or settings.INSTANCE == 'prod'):
        hn = get_host_no_port(request)

    if isinstance(response, HttpResponseRedirect):
        return HttpResponseRedirect(urlparse.urljoin('http://'+hn+'/',response['Location']))
    return response


def upgrade_to_https_and_downgrade_upon_redirect(view):
    '''This decorator will make sure that the view, if accessed over http, will get upgrade to https
        Any subsequent redirects returned by this view will get downgraded
    '''
    @wraps (view)
    def inner(request, *args, **kw):
        #explicitly upgrading
        hn = request.get_host()
        if (settings.INSTANCE == 'stage' or settings.INSTANCE == 'prod'):
            hn = get_host_no_port(request)

        if (settings.INSTANCE == 'stage' or settings.INSTANCE == 'prod') and not request.is_secure():
            return redirect('https://'+hn+request.get_full_path())
        return redirects_use_http(view(request, *args, **kw),request)
    return inner
