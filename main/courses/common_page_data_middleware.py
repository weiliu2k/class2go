from courses.common_page_data import get_common_page_data
from django.http import Http404
from c2g.models import Course

import logging
logger = logging.getLogger(__name__)

class common_data(object):
    """
    This is a middleware class that eagerly retrieves page data that might be common to most requests.  It is 
    basically a wrapper around Sherif's implementation of common_page_data.  The data is stored as a field of 
    request.
    """
    def process_view (self, request, view_func, view_args, view_kwargs):
        if ('course_prefix' in view_kwargs) and \
           ('course_suffix' in view_kwargs):
            cp = view_kwargs['course_prefix']
            cs = view_kwargs['course_suffix']
        else:
            #No course information in the URL.  There is a special case that has it as a POST parameter (Why?)
            #Handle those here
            if request.POST.get('course_prefix', None) and \
               request.POST.get('course_suffix', None):
                #The course info is in the POST in this case
                cp = request.POST.get('course_prefix')
                cs = request.POST.get('course_suffix')
            else:
                return None
    
        try:
            request.common_page_data=get_common_page_data(request, cp, cs)
            return None
        except Course.DoesNotExist:
            raise Http404
