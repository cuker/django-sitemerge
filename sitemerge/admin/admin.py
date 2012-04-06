from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from sitemerge.models import ContentMerge

class ContentMergeAdmin(admin.ModelAdmin):
    list_display = ('status', 'content_type', 'action', 'completion_timestamp')
    list_filter = ('status', 'content_type', 'action', 'completion_timestamp')
    actions = ['execute_merge', 'schedule_merge']
    
    def execute_merge(self, request, queryset):
        count = 0
        for obj in queryset:
            obj.schedule_merge(immediate=True)
            count += 1
        self.message_user(request, "%s content merges(s) queued for loading." % count)
    execute_merge.short_description = _('Execute Merge')
    
    def schedule_merge(self, request, queryset):
        count = 0
        for obj in queryset:
            obj.schedule_merge()
            count += 1
        self.message_user(request, "%s content merges(s) scheduled for loading." % count)
    schedule_merge.short_description = _('Schedule Merge')

admin.site.register(ContentMerge, ContentMergeAdmin)

