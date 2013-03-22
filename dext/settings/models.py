# coding: utf-8

from django.db import models


class Setting(models.Model):

    key = models.CharField(max_length=64, unique=True, db_index=True)
    value = models.TextField(default='')
