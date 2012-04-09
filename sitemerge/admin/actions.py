from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from forms import ScheduleMergeForm

def schedule_merge(modeladmin, request, queryset):
    form = None
    if 'apply' in request.POST:
        form = ScheduleMergeForm(request.POST)
        
        if form.is_valid():
            content_merge = form.save(request.user, queryset)
            content_merge.schedule_merge()
            #send message
            message = '%s item(s) scheduled for merging' % queryset.count()
            messages.add_message(request, messages.SUCCESS, message)
            return HttpResponseRedirect(reverse('admin:sitemerge_contentmerge_change', args=[content_merge.pk]))
    else:
        form = ScheduleMergeForm(initial=request.POST)
    return TemplateResponse(request, 'admin/sitemerge/schedule_merge.html', {'form':form, 'queryset':queryset})

