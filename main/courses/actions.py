from datetime import datetime
from os.path import basename

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.utils.functional import wraps

from courses.course_materials import get_course_materials
from courses.common_page_data import get_common_page_data
from courses.forms import *
from c2g.models import *
import settings


def auth_view_wrapper(view):
    @wraps (view)
    def inner(request, *args, **kw):
        user = request.user
        course = request.common_page_data['course']

        if user.is_authenticated() and not is_member_of_course(course, user):
            messages.add_message(request,messages.ERROR, 'You must be a member of the course to view the content you chose.')      
            return HttpResponseRedirect(reverse('courses.views.main', args=(request.common_page_data['course_prefix'], request.common_page_data['course_suffix'],)) + "?join_next=" + request.path)

        if not user.is_authenticated():
            messages.add_message(request,messages.ERROR, 'You must be logged-in to view the content you chose.')
            if settings.SITE_NAME_SHORT == "Stanford":
                if course.institution_only:
                    return HttpResponseRedirect(reverse('shib_login') + "?next=" + request.path)
                else:
                    return HttpResponseRedirect(reverse('auth_login') + "?next=" + request.path)                        
            return HttpResponseRedirect(reverse('default_login') + "?next=" + request.path)

        headless = request.GET.get('headless')
        if headless is not None:
            if headless == '1':
                request.session['headless'] = headless
            elif headless == '0':
                #headless explicitly turned off
                request.session['headless'] = None

        return view(request, *args, **kw)
    return inner

def auth_can_switch_mode_view_wrapper(view):
    @wraps (view)
    def inner(request, *args, **kw):
        if request.common_page_data['can_switch_mode']:
            return view(request, *args, **kw)
        else:
            messages.add_message(request,messages.ERROR, "You don't have permission to view that content.")
            return HttpResponseRedirect(reverse('courses.views.main', args=(request.common_page_data['course_prefix'], request.common_page_data['course_suffix'],)))
    return inner

def auth_is_course_admin_view_wrapper(view):
    @wraps (view)
    def inner(request, *args, **kw):
        if request.common_page_data['is_course_admin']:
            return view(request, *args, **kw)
        else:
            messages.add_message(request,messages.ERROR, "You don't have permission to view that content.")
            return HttpResponseRedirect(reverse('courses.views.main', args=(request.common_page_data['course_prefix'], request.common_page_data['course_suffix'],)))
    return inner

def auth_is_staff_view_wrapper(view):
    @wraps (view)
    def inner(request, *args, **kw):
        user = request.user
        if user.is_staff:
            return view(request, *args, **kw)
        else:
           raise Http404
    return inner                

def create_contentgroup_entries_from_post(request, postparam, ready_obj, ready_obj_tag, display_style="list"):
    """Given a post, ready object and parenting info, add ContentGroups

    request: a django request object with POST parameters we can extract parent info from
    postparam: the parameter in the POST we expect to find parent info in
    ready_obj: The ready-mode object reference to be added to the ContentGroup table
    ready_obj_tag: The text description, in the style of ContentGroup.groupable_types, of ready_obj
    display_style: how the child should be displayed (optional, defaults to 'list')
    """
    parent_tag, parent_id = None,None
    parent_tag = request.POST.get(postparam)
    if parent_tag and parent_tag != 'none,none':
        parent_tag,parent_id = parent_tag.split(',')
        parent_id = long(parent_id)
    if parent_tag == "none,none" or parent_tag == None:                   # make this object the parent
        content_group_groupid = ContentGroup.add_parent(ready_obj.course, ready_obj_tag, ready_obj) # add_parent should handle special cases already
    else:
        parent_ref = ContentGroup.groupable_types[parent_tag].objects.get(id=long(parent_id))
        if (parent_ref.mode != 'ready'):
            parent_ref = parent_ref.image
        content_group_groupid = ContentGroup.add_parent(parent_ref.course, parent_tag, parent_ref)
        ContentGroup.add_child(content_group_groupid, ready_obj_tag, ready_obj, display_style=display_style)
    return content_group_groupid

@require_POST
@auth_can_switch_mode_view_wrapper
def switch_mode(request):
    request.session['course_mode'] = request.POST.get('to_mode')
    return redirect(request.META['HTTP_REFERER'])

def always_switch_mode(view):
    """Check whether we're in draft mode, and if we're not, switch to it."""
    # Sadly the wrapper name is a bit of a misnomer, should be 'always_draft_mode'
    wrapped_function_path = '.'.join((view.__module__, view.__name__))
    @wraps(view)
    def do_mode_switch(request, *args, **kw):
        current_mode = request.session.get('course_mode', 'unknown state')
        if current_mode == 'draft':
            return view(request, *args, **kw)
        request.session['course_mode'] = 'draft'
        course_prefix = kw.get('course_prefix', None) or request.POST.get('course_prefix', None) or request.common_page_data.get('course_prefix', '')
        course_suffix = kw.get('course_suffix', None) or request.POST.get('course_suffix', None) or request.common_page_data.get('course_suffix', '')
        if course_prefix == '' or course_suffix == '':
            print "WARNING: empty course_prefix or course_suffix in view decorator always_switch_mode, wrapping %s." % wrapped_function_path
        request.common_page_data = get_common_page_data(request, course_prefix, course_suffix)
        return view(request, *args, **kw)
    return do_mode_switch

@require_POST
@auth_is_course_admin_view_wrapper
@always_switch_mode     # not strictly necessary, but good for consistency
def add_section(request):
    common_page_data = request.common_page_data

    index = len(ContentSection.objects.filter(course=common_page_data['course']))

    draft_section = ContentSection(course=common_page_data['draft_course'], title=request.POST.get("title"), index=index, mode='draft')
    draft_section.save()
    draft_section.create_ready_instance()

    return redirect(request.META['HTTP_REFERER'])

@require_POST
@auth_is_course_admin_view_wrapper
def commit(request):
    ids = request.POST.get("commit_ids").split(",")
    for id in ids:
        parts = id.split('_')
        if parts[0] == 'video':
            Video.objects.get(id=parts[1]).commit()
        elif parts[0] == 'problemset':
            ProblemSet.objects.get(id=parts[1]).commit()
        elif parts[0] == 'additionalpage':
            AdditionalPage.objects.get(id=parts[1]).commit()
        elif parts[0] == 'exam':
            Exam.objects.get(id=parts[1]).commit()
    return redirect(request.META['HTTP_REFERER'])

@require_POST
@auth_is_course_admin_view_wrapper
def revert(request):
    ids = request.POST.get("revert_ids").split(",")
    for id in ids:
        parts = id.split('_')
        if parts[0] == 'video':
            Video.objects.get(id=parts[1]).revert()
        elif parts[0] == 'problemset':
            ProblemSet.objects.get(id=parts[1]).revert()
        elif parts[0] == 'additionalpage':
            AdditionalPage.objects.get(id=parts[1]).revert()
        elif parts[0] == 'exam':
            Exam.objects.get(id=parts[1]).revert()
    return redirect(request.META['HTTP_REFERER'])

@require_POST
@auth_is_course_admin_view_wrapper
def change_live_datetime(request):
    list_type = request.POST.get('list_type')
    action = request.POST.get('action')
    form = LiveDateForm(request.POST)
    if form.is_valid():
        if action == "Make Ready and Go Live":
            new_live_datetime = datetime.now()
        elif action == "Set Live Date":
            new_live_datetime = form.cleaned_data['live_datetime']
        else:
            new_live_datetime = None

        ids = request.POST.get("change_live_datetime_ids").split(",")

        for id in ids:
            parts = id.split('_')
            if parts[0] == 'video':
                content = Video.objects.get(id=parts[1])
            elif parts[0] == 'problemset':
                content = ProblemSet.objects.get(id=parts[1])
            elif parts[0] == 'additionalpage':
                content = AdditionalPage.objects.get(id=parts[1])
            elif parts[0] == 'file':
                content = File.objects.get(id=parts[1])
            elif parts[0] == 'exam':
                content = Exam.objects.get(id=parts[1])

            if action == "Make Ready and Go Live" and parts[0] != 'file':
                content.commit()
            content.live_datetime = new_live_datetime
            content.image.live_datetime = new_live_datetime
            content.save()
            content.image.save()

        if list_type == 'course_materials':
            return redirect('courses.views.course_materials', request.common_page_data['course_prefix'], request.common_page_data['course_suffix'])
        elif list_type == 'problemsets':
            return redirect('problemsets.views.listAll', request.common_page_data['course_prefix'], request.common_page_data['course_suffix'])
        else:
            return redirect('courses.videos.views.list', request.common_page_data['course_prefix'], request.common_page_data['course_suffix'])
        #This won't work anymore because referer could be /change_live_datetime if it's an invalid form post
        #return redirect(request.META['HTTP_REFERER'])

    if list_type == 'course_materials':
        section_structures = get_course_materials(common_page_data=request.common_page_data, get_video_content=True, get_pset_content=True, get_additional_page_content=True, get_file_content=True, get_exam_content=True)
        template = 'courses/draft/course_materials.html'
    elif list_type == 'problemsets':
        section_structures = get_course_materials(common_page_data=request.common_page_data, get_pset_content=True)
        template = 'problemsets/draft/list.html'
    else:
        section_structures = get_course_materials(common_page_data=request.common_page_data, get_video_content=True)
        template = 'videos/draft/list.html'
    return render(request, template,
                  {'common_page_data': request.common_page_data,
                   'section_structures': section_structures,
                   'form': form})

@require_POST
@auth_is_course_admin_view_wrapper
def check_filename(request, course_prefix, course_suffix, file_type):
    filename = request.POST.get('filename')
    
    if file_type == "files":
        #Validate that file doesn't already exist for course
        files = File.objects.getByCourse(course=request.common_page_data['course'])
        for file in files:
            if basename(file.file.name) == filename:
                return HttpResponse("File name already exists!")
    else:
        exercises = Exercise.objects.filter(handle=course_prefix+"--"+course_suffix,is_deleted=0)
        for exercise in exercises:
            if exercise.fileName == filename:
                #File name already exists, check if it has been taken yet
                if ProblemActivity.objects.filter(Q(video_to_exercise__exercise=exercise) | Q(problemset_to_exercise__exercise=exercise)).exists():
                    return HttpResponse("File name already exists! Exercise taken")
                else:
                    return HttpResponse("File name already exists!")

    return HttpResponse("File name is available")            

def is_member_of_course(course, user):
    student_group_id = course.student_group.id
    instructor_group_id = course.instructor_group.id
    tas_group_id = course.tas_group.id
    readonly_tas_group_id = course.readonly_tas_group.id

    group_list = user.groups.values_list('id',flat=True)

    for item in group_list:
        if item == student_group_id or item == instructor_group_id or item == tas_group_id or item == readonly_tas_group_id:
            return True

    return False


@require_POST
@csrf_protect
def signup_with_course(request, course_prefix, course_suffix):
    course = request.common_page_data['course']
    draft_course = course if course.mode == "draft" else course.image

    if course.institution_only and (course.institution not in request.user.get_profile().institutions.all()):
        messages.add_message(request,messages.ERROR, 'Registration in this course is restricted to ' + course.institution.title + '.  Perhaps you need to logout and login with your '+ course.institution.title + ' credentials?')
        return redirect(reverse('courses.views.main',args=[course_prefix,course_suffix]))

    invites = StudentInvitation.objects.filter(course=draft_course, email=request.user.email)

    if course.preenroll_only and not invites.exists():
        messages.add_message(request,messages.ERROR, 'Sorry!  Registration in this course is restricted, and we did not find your email in the access list.  Please contact the course staff if you believe this to be an error.')
        return redirect(reverse('courses.views.main',args=[course_prefix,course_suffix]))

    if request.user.is_authenticated() and (not is_member_of_course(course, request.user)):
        student_group = Group.objects.get(id=course.student_group_id)
        student_group.user_set.add(request.user)
        #now remove any invitations
        for invite in invites:
            invite.delete()
    if (request.GET.__contains__('redirect_to')):
        return redirect(request.GET.get('redirect_to'))
    return redirect(reverse('courses.views.main',args=[course_prefix,course_suffix]))


@require_POST
def signup(request):
    handle = request.POST.get('handle')

    user = request.user
    course = Course.objects.get(handle=handle, mode = "ready")
    if not is_member_of_course(course, user):
        student_group = Group.objects.get(id=course.student_group_id)
        student_group.user_set.add(user)

    return redirect(request.META['HTTP_REFERER'])



