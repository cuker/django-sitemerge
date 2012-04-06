from django.dispatch import dispatcher

content_merge_executed = dispatcher.Signal(providing_args=["instance"])

