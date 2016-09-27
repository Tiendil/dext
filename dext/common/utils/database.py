# coding: utf-8
from django.db import connection, transaction

@transaction.atomic()
def raw_save(record):

    cursor = connection.cursor()

    sql = ["UPDATE %s SET" % record._meta.db_table]
    args = []
    for j, field in enumerate(record._meta.fields):
        sql.extend(['"%s"' % field.column, ' = ', '%s'])
        args.append(field.get_prep_value(getattr(record, field.attname)))
        if j != len(record._meta.fields) - 1:
            sql.append(',')

    sql.append('WHERE id = %s')
    args.append(record.id)
    sql = ' '.join(sql)

    cursor.execute(sql, args)
