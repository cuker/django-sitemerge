from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from sitemerge.models import ContentMerge, SiteMergeProfile, ContentMergeBatch

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
            'fields': ('name', 'merge_action', 'status', 'scheduled_timestamp', 'content_type', 'site_field', 'src_site', 'dst_site', 'log', 'task_id', 'completion_timestamp')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('object_ids',)
        }),
     )
    actions = ['create_or_update_content_merge', 'execute_merge', 'schedule_merge']
    
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

    def create_or_update_content_merge(self, request ,queryset):
        count = 0
        for obj in queryset:
            obj.create_or_update_content_merge()
            count += 1
        if count > 0:
            self.message_user(request, "Content Merge created")
        else:
            self.message_user(request, "Please select a ContentMergePorfile")
    create_or_update_content_merge.short_description = _('Create or update ContentMerge')

admin.site.register(SiteMergeProfile, SiteMergeProfileAdmin)

admin.site.register(ContentMergeBatch)