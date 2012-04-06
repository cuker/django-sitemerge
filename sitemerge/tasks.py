from celery.task import task
from models import ContentMerge

@task()
def execute_merge(pk):
    merge = ContentMerge.objects.get(pk=pk)
    merge.execute_merge()


