from django.db import models, transaction
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
import json

from signals import content_merge_executed

import sys, traceback

import datetime
import logging

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

MERGE_ACTIONS = [('swap', 'Swap'),
                 ('sync', 'Sync'),]

STATUS_CHOICES = [('pending', 'Pending'),
                  ('error', 'Error'),
                  ('complete', 'Complete'),]

class SiteMergeProfile(models.Model):
    name = models.CharField(max_length=255)
    merge_action = models.CharField(choices=MERGE_ACTIONS, max_length=5)
    scheduled_timestamp = models.DateTimeField(null=True, blank=True)
    content_type = models.ManyToManyField(ContentType)
    src_site = models.ForeignKey(Site, verbose_name='source site', related_name='sitemergeprofile_sources')
    dst_site = models.ForeignKey(Site, verbose_name='destination site', related_name='sitemergeprofile_destinations')

    def __unicode__(self):
        return self.name

    def create_batch(self, user=None, run=False):
        batch = ContentMergeBatch(site_merge_profile=self, created_by=user)
        batch.save()
        for content_type in self.content_type.all():
            content_merge = ContentMerge(batch=batch, content_type=content_type)
            content_merge.merge_action = self.merge_action
            content_merge.scheduled_timestamp = self.scheduled_timestamp
            content_merge.site_field = "sites"
            content_merge.src_site = self.src_site
            content_merge.dst_site = self.dst_site
            content_merge.save()
            if run:
                content_merge.schedule_merge(True)
        return batch


class ContentMergeBatch(models.Model):
    site_merge_profile = models.ForeignKey(SiteMergeProfile)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, blank=True)
    
    def __unicode__(self):
        return "%s - created at %s by %s" % (self.site_merge_profile.name, self.created_at, self.created_by) 
    
    def run(self, immediate=False):
        for content_merge in self.contentmerge_set.all():
            content_merge.schedule_merge(immediate)
    
    
class ContentMerge(models.Model):
    merge_action = models.CharField(choices=MERGE_ACTIONS, max_length=5)
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default='pending')
    scheduled_timestamp = models.DateTimeField(null=True, blank=True)
    completion_timestamp = models.DateTimeField(null=True, blank=True)
    scheduled_by = models.ForeignKey(User, blank=True, null=True)
    content_type = models.ForeignKey(ContentType)
    object_ids = models.TextField(blank=True, help_text='JSON encoded query kwargs') #TODO advanced
    site_field = models.CharField(blank=True, max_length=32)
    log = models.TextField(blank=True)

    batch = models.ForeignKey(ContentMergeBatch, blank=True, null=True)

    src_site = models.ForeignKey(Site, verbose_name='source site', related_name='contentmerge_sources')
    dst_site = models.ForeignKey(Site, verbose_name='destination site', related_name='contentmerge_destinations')

    task_id = models.CharField(max_length=128, blank=True)

    def schedule_merge(self, immediate=False):
        if self.task_id:
            pass #TODO cancel task
        self.status = 'pending'
        self.completion_timestamp = None
        self.save()
        from tasks import execute_merge
        if not immediate and self.scheduled_timestamp:
            task = execute_merge.delay(self.pk, eta=self.scheduled_application_timestamp)
        else:
            task = execute_merge.delay(self.pk)
        type(self).objects.filter(pk=self.pk).update(task_id=task.task_id)
        return task

    def prepare_logger(self):
        logger = logging.Logger('sitemerge.models')
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        logger.addHandler(handler)
        def read_log():
            return stream.getvalue()
        logger.read_log = read_log
        return logger

    @transaction.commit_on_success
    def execute_merge(self):
        logger = self.prepare_logger()
        try:
            if self.merge_action == 'swap':
                self.swap_sites(logger)
            elif self.merge_action == 'sync':
                self.sync_sites(logger)
        except Exception, exception:
            typ, val, tb = sys.exc_info()
            message = traceback.format_exception_only(typ, val)[0]
            body = traceback.format_exc()
            logger.error('Unhandled Exception: %s' % '\n'.join([message, body]))
            self.status = 'error'
            transaction.rollback()
        else:
            self.status = 'complete'
        finally:
            self.log = logger.read_log()
            self.completion_timestamp = datetime.datetime.now()
            self.save()
            transaction.commit()
        content_merge_executed.send(sender=type(self), instance=self)

    def set_queryset(self, queryset):
        model = queryset.model
        self.content_type = ContentType.objects.get_for_model(model)
        object_ids = list(queryset.values_list('pk', flat=True))
        self.object_ids = json.dumps({'pk__in':object_ids})

    def get_queryset(self):
        model = self.content_type.model_class()
        params = {}
        if self.object_ids:
            params = json.loads(self.object_ids)
        qs = model.objects.filter(**params)
        return qs

    def get_site_field(self):
        model = self.content_type.model_class()
        if self.site_field:
            return model._meta.get_field(self.site_field)

        for field in model._meta.fields:
            if getattr(field, 'related', None):
                if field.related.parent_model == Site:
                    return field

    def is_m2m(self):
        field = self.get_site_field()
        return isinstance(field, models.ManyToManyField)

    def swap_sites(self, logger):
        queryset = self.get_queryset()
        site_field = self.get_site_field()

        src_only = queryset.filter(**{site_field.name: self.src_site})
        dst_only = queryset.filter(**{site_field.name: self.dst_site})

        if self.is_m2m():
            # Execute dst_only queryset initially so that we don't scoop up the recently
            # swapped ones in the second pass
            src_only = src_only.exclude(**{site_field.name: self.dst_site})
            dst_only = [o for o in dst_only.exclude(**{site_field.name: self.src_site})]
            #TODO ideally do an update on the m2m table
            for entry in src_only:
                manager = getattr(entry, site_field.name)
                manager.remove(self.src_site)
                manager.add(self.dst_site)
                logger.info('Moved %s (%s) from %s to %s' % (entry, entry.pk, self.src_site, self.dst_site))

            for entry in dst_only:
                manager = getattr(entry, site_field.name)
                manager.remove(self.dst_site)
                manager.add(self.src_site)
                logger.info('Moved %s (%s) from %s to %s' % (entry, entry.pk, self.dst_site, self.src_site))
        else:
            #TODO log the object ids
            count = src_only.update(**{site_field.name: self.dst_site})
            logger.info('Moved %s entries to %s' % (count, self.dst_site))

            count = dst_only.update(**{site_field.name: self.src_site})
            logger.info('Moved %s entries to %s' % (count, self.src_site))

    def sync_sites(self, logger):
        #copy src into dst
        queryset = self.get_queryset()
        site_field = self.get_site_field()

        src_only = queryset.filter(**{site_field.name: self.src_site})

        if self.is_m2m():
            src_only = src_only.exclude(**{site_field.name: self.dst_site})
            for entry in src_only:
                manager = getattr(entry, site_field.name)
                manager.add(self.dst_site)
                logger.info('Added %s to %s' % (entry, self.dst_site))
        else:
            #TODO log the object ids
            count = src_only.update(**{site_field.name: self.dst_site})
            logger.info('Moved %s entries to %s' % (count, self.dst_site))

