# coding: utf-8
from django.db import connection, transaction

def raw_save(record):

    cursor = connection.cursor()

    sql = ["UPDATE %s SET" % record._meta.db_table]
    args = []
    for j, field in enumerate(record._meta.fields):
        sql.extend(['"%s"' % field.column, ' = ', '%s'])
        args.append(getattr(record, field.attname))
        if j != len(record._meta.fields) - 1:
            sql.append(',')

    sql.append('WHERE id = %s')
    args.append(record.id)
    sql = u' '.join(sql)

    cursor.execute(sql, args)
    transaction.commit_unless_managed()
