# coding: utf-8

from django.db import models



class Relation(models.Model):
    relation = models.IntegerField(db_index=True)

    from_type = models.IntegerField()
    from_object = models.BigIntegerField()

    to_type = models.IntegerField()
    to_object = models.BigIntegerField()

    class Meta:
        index_together = ( ('from_type', 'from_object'),
                           ('to_type', 'to_object')  )
