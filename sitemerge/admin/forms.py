from django import forms
from django.contrib.admin import widgets

from sitemerge.models import ContentMerge

class ScheduleMergeForm(forms.ModelForm):
    #for admin actions
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    action = forms.CharField(widget=forms.MultipleHiddenInput)
    select_across = forms.IntegerField(widget=forms.HiddenInput, required=False)
    #TODO scheduled_timestamp gets admin datetime widget
    scheduled_timestamp = forms.DateTimeField(widget=widgets.AdminSplitDateTime, required=False)
    
    def clean(self):
        if 'src_site' in self.cleaned_data and 'dst_site' in self.cleaned_data:
            if self.cleaned_data['src_site'] == self.cleaned_data['dst_site']:
                raise forms.ValidationError('The source site must be different from the destination site')
        
        #TODO detect if site_field is needed
        
        return self.cleaned_data
    
    def save(self, user, queryset, commit=True):
        instance = super(ScheduleMergeForm, self).save(commit=False)
        instance.scheduled_by = user
        instance.set_queryset(queryset)
        if commit:
            instance.save()
        return instance
    
    class Meta:
        model = ContentMerge
        fields = ['merge_action', 'src_site', 'dst_site', 'site_field', 'scheduled_timestamp']
