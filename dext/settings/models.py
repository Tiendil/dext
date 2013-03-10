# coding: utf-8

from django.db import models
from django.dispatch import receiver


class Setting(models.Model):

    key = models.CharField(max_length=64, unique=True, db_index=True)
    value = models.TextField(default='')



@receiver(models.signals.post_save, dispatch_uid='dext_settings_post_save')
def dext_settings_post_save(sender, **kwargs):
    from dext.settings import settings
    settings.refresh(force=True)

@receiver(models.signals.post_delete, dispatch_uid='dext_settings_post_delete')
def dext_settings_post_delete(sender, **kwargs):
    from dext.settings import settings
    settings.refresh(force=True)
