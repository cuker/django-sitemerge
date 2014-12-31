from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from sitemerge.models import ContentMerge, SiteMergeProfile

class ContentMergeAdmin(admin.ModelAdmin):
    list_display = ('status', 'content_type', 'merge_action', 'completion_timestamp')
    list_filter = ('status', 'content_type', 'merge_action', 'completion_timestamp')
    actions = ['execute_merge', 'schedule_merge']
    readonly_fields = ['log', 'task_id', 'completion_timestamp']
    
    fieldsets = (
        (None, {
            'fields': ('merge_action', 'status', 'scheduled_timestamp', 'scheduled_by', 'content_type', 'site_field', 'src_site', 'dst_site', 'log', 'task_id', 'completion_timestamp')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('object_ids',)
        }),
    )
    
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

class SiteMergeProfileAdmin(admin.ModelAdmin):
    readonly_fields = ['status', 'log', 'task_id', 'completion_timestamp']
    fieldsets = (
        (None, {
            'fields': ('merge_action', 'status', 'scheduled_timestamp', 'content_type', 'site_field', 'src_site', 'dst_site', 'log', 'task_id', 'completion_timestamp')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('object_ids',)
        }),
     )

admin.site.register(SiteMergeProfile, SiteMergeProfileAdmin)

