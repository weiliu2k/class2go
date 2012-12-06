from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from c2g.models import *
from courses.course_materials import get_course_materials
from courses.common_page_data import get_common_page_data
import re
from django.contrib import messages
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from courses.forms import *

from courses.actions import auth_view_wrapper

from urlparse import urlparse
import settings

def main(request):
    return render_to_response('chat/chat.html',
            {},
            context_instance=RequestContext(request))
