from sitemerge.models import ContentMerge, SiteMergeProfile, ContentMergeBatch

from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.contenttypes.models import ContentType
from django.forms.models import ModelForm, ModelMultipleChoiceField
from django.utils.translation import ugettext_lazy as _


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

class ContentTypeChoiceField(ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs["widget"] = FilteredSelectMultiple("Person", False)
        super(ContentTypeChoiceField, self).__init__(*args, **kwargs)
        
    
    def label_from_instance(self, obj):
        return "%s (%s)" % (obj.name, obj.app_label)
    
class EditForm(ModelForm):
    content_type = ContentTypeChoiceField([""])
    
    class Meta:
        model = SiteMergeProfile
        
    def __init__(self, *args, **kwargs):
        super(EditForm, self).__init__(*args, **kwargs)
        # NOTE this will only apply to m2ms called "sites", not single FKs like in Redirects
        valid_model_ids = [ct.id for ct in ContentType.objects.all().order_by("model") if hasattr(ct.model_class(), "sites")]
        self.fields['content_type'].queryset = ContentType.objects.filter(id__in=valid_model_ids).order_by("name")

class SiteMergeProfileAdmin(admin.ModelAdmin):
    form = EditForm
    actions = ['create_batch', 'create_and_run_batch']
    
    def create_and_run_batch(self, request, queryset):
        self.create_batch(request, queryset, run=True)
        self.message_user(request, ("Running created batch(es)"))
    
    def create_batch(self, request, queryset, run=False):
        for obj in queryset:
            obj.create_batch(user=request.user, run=run)
        self.message_user(request, ("Batch for %s created" % obj))

admin.site.register(SiteMergeProfile, SiteMergeProfileAdmin)

class ContentMergeBatchAdmin(admin.ModelAdmin):
    actions = ['run']
    readonly_fields = ['created_by']
    
    def run(self, request, queryset):
        for obj in queryset:
            obj.run()
            self.message_user(request, ("Running %s" % obj))
admin.site.register(ContentMergeBatch,ContentMergeBatchAdmin)
