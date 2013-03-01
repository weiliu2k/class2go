from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_slug
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from c2g.models import *
from courses.common_page_data import get_common_page_data
from courses.actions import always_switch_mode, auth_is_course_admin_view_wrapper, create_contentgroup_entries_from_post


@require_POST
@auth_is_course_admin_view_wrapper
@always_switch_mode     # Not strictly necessary, but good for consistency
def add(request):
    def redirectWithError(warn_msg):
        messages.add_message(request,messages.ERROR, warn_msg)
        return redirect(request.META['HTTP_REFERER'])
    
    course_prefix = request.POST.get("course_prefix")
    course_suffix = request.POST.get("course_suffix")
    common_page_data = get_common_page_data(request, course_prefix, course_suffix)
    
    
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.view', course_prefix, course_suffix)
    
    menu_slug = None
    if request.POST.get("menu_slug") != "":
        menu_slug = request.POST.get("menu_slug")
        
    section = None
    if request.POST.get("section_id") != "":
        section = ContentSection.objects.get(id=request.POST.get("section_id"))

    if request.POST.get("menu_slug") != "":
        index = len(AdditionalPage.objects.filter(course=common_page_data['course'],menu_slug=request.POST.get("menu_slug")))
    else:
        index = section.getNextIndex()
    
    #Validate manually, b/c we didn't use django forms here since we missed it
    try:
        validate_slug(request.POST.get("slug"))
    except ValidationError:
        return redirectWithError("The url descriptor cannot be empty and can only contain numbers, letters, underscores, and hyphens")

    if AdditionalPage.objects.filter(course=common_page_data['course'], slug=request.POST.get("slug")).exists():
        return redirectWithError("A page with this URL identifier already exists")

    if len(request.POST.get("title")) == 0:
        return redirectWithError("The title cannot be empty")

    if len(request.POST.get("title")) > AdditionalPage._meta.get_field("title").max_length:
        return redirectWithError("The title length was too long")

    draft_page = AdditionalPage(course=common_page_data['draft_course'], menu_slug=menu_slug, section=section, title=request.POST.get("title"), slug=request.POST.get("slug"), index=index, mode='draft')
    draft_page.save()
    draft_page.create_ready_instance()

    create_contentgroup_entries_from_post(request, 'parent_id', draft_page.image, 'additional_page', display_style='list')

    if request.POST.get("menu_slug") == "":
        return redirect('courses.views.course_materials', course_prefix, course_suffix)
    else:
        return redirect(request.META['HTTP_REFERER'])

@require_POST
@auth_is_course_admin_view_wrapper
@always_switch_mode     # Not strictly necessary, but good for consistency
def save(request):
    def redirectWithError(warn_msg):
        messages.add_message(request,messages.ERROR, warn_msg)
        return redirect(request.META['HTTP_REFERER'])
    
    common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    if not common_page_data['is_course_admin']:
        return redirect('courses.views.main', common_page_data['course_prefix'],common_page_data['course_suffix'])
    
    page = AdditionalPage.objects.get(id=request.POST.get("page_id"))
    if request.POST.get("revert") == '1':
        page.revert()
    else:
        #Validate manually, b/c we didn't use django forms here since we missed it
        try:
            validate_slug(request.POST.get("slug"))
        except ValidationError:
            return redirectWithError("The url descriptor cannot be empty and can only contain numbers, letters, underscores, and hyphens")

        if (not page.slug==request.POST.get("slug")) and AdditionalPage.objects.filter(course=common_page_data['course'], slug=request.POST.get("slug")).exists():
            return redirectWithError("A page with this URL identifier already exists")

        if len(request.POST.get("title")) == 0:
            return redirectWithError("The title cannot be empty")

        if len(request.POST.get("title")) > AdditionalPage._meta.get_field("title").max_length:
            return redirectWithError("The title length was too long")

        new_section = request.POST.get("section")
        old_section = page.section
        if new_section is None or new_section == "null":                # Topbar pages
            page.section = None
            page.menu_slug = "course_info"       # normal pages
        else:
            page.section = ContentSection.objects.get(id=new_section)
            page.menu_slug = None

        page.title = request.POST.get("title")
        page.description = request.POST.get("description")
        page.slug = request.POST.get("slug")
        page.save()

        ##Also save the production slug per Issue #685, basically slugs are not stageable.
        page.image.slug = request.POST.get("slug")
        page.image.save()

        create_contentgroup_entries_from_post(request, 'parent', page.image, 'additional_page', display_style='list')

        if request.POST.get("commit") == '1':
            page.commit()
            
        if request.POST.get("title") == 'Overview':
            
            ready_course = common_page_data['ready_course']
            draft_course = common_page_data['draft_course']


            draft_course.outcomes = request.POST.get("outcomes")
            draft_course.faq = request.POST.get("faq")
            draft_course.prerequisites = request.POST.get("prerequisites")
            draft_course.accompanying_materials = request.POST.get("accompanying_materials")
            draft_course.description = request.POST.get("description")
            draft_course.save()
                
            if request.POST.get("commit") == '1': 
                ready_course.outcomes = request.POST.get("outcomes")
                ready_course.faq = request.POST.get("faq")
                ready_course.prerequisites = request.POST.get("prerequisites")
                ready_course.accompanying_materials = request.POST.get("accompanying_materials")
                ready_course.description = request.POST.get("description")
                ready_course.save()
    
                   
        # This has to happen last of all
        if (old_section != None or new_section != None) and (old_section or new_section != "null"):
            ContentGroup.reassign_parent_child_sections('additional_page', page.image.id, new_section)

    return redirect('courses.additional_pages.views.main', common_page_data['course_prefix'],common_page_data['course_suffix'], page.slug)

@require_POST
@auth_is_course_admin_view_wrapper
@always_switch_mode
def save_order(request):
    common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    if not common_page_data['is_course_admin']:
        redirect('courses.views.main', common_page_data['course_prefix'],common_page_data['course_suffix'])
    
    pages = AdditionalPage.objects.filter(course=common_page_data['draft_course'])
    for page in pages:
        page.index = request.POST.get("order_"+str(page.id))
        page.save()
        prod_page = page.image
        prod_page.index = request.POST.get("order_"+str(page.id))
        prod_page.save()
        
    return redirect(request.META['HTTP_REFERER'])
    
@require_POST
@auth_is_course_admin_view_wrapper
@always_switch_mode     # Not strictly necessary, but good for consistency
def delete(request):
    common_page_data = get_common_page_data(request, request.POST.get("course_prefix"), request.POST.get("course_suffix"))
    if not common_page_data['is_course_admin']:
        redirect('courses.views.main', common_page_data['course_prefix'],common_page_data['course_suffix'])
        
    page_id = request.POST.get("page_id")
    page = AdditionalPage.objects.get(id=page_id)
    if page.slug == 'overview':
        return
        
    page.delete()
    if page.image:
        page.image.delete()
    
    if request.POST.get("menu_slug") == "":
        return redirect('courses.views.course_materials', course_prefix, course_suffix)
    else:
        return redirect(request.META['HTTP_REFERER'])
