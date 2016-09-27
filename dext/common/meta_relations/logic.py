# coding: utf-8
import re

from dext.common.utils import discovering

from . import objects
from . import exceptions
from . import models


_RELATIONS = {}
_TYPES = {}

_UID_REGEX = re.compile(r'(\d+)#(\d+)')


def _register_meta_relations(container, candidates):

    for candidate in discovering.discover_classes(candidates, objects.MetaRelation):
        if candidate.TYPE in container:
            raise exceptions.DuplicateRelationError(type=candidate.TYPE)
        if candidate.TYPE is None:
            continue
        container[candidate.TYPE] = candidate


@discovering.automatic_discover(_RELATIONS, 'meta_relations')
def autodiscover_relations(container, module):
    _register_meta_relations(container, [getattr(module, name) for name in dir(module)])


def _register_meta_types(container, candidates):

    for candidate in discovering.discover_classes(candidates, objects.MetaType):
        if candidate.TYPE in container:
            raise exceptions.DuplicateTypeError(type=candidate.TYPE)
        if candidate.TYPE is None:
            continue
        container[candidate.TYPE] = candidate


@discovering.automatic_discover(_TYPES, 'meta_relations')
def autodiscover_types(container, module):
    _register_meta_types(container, [getattr(module, name) for name in dir(module)])


def create_uid(type_id, object_id):
    return '%s#%s' % (type_id, object_id)

def get_object(type_id, object_id):
    if type_id not in _TYPES:
        raise exceptions.WrongTypeError(type=type_id)

    object = _TYPES[type_id].create_from_id(object_id)

    if object is None:
        raise exceptions.WrongObjectError(type=type_id, object=object_id)

    return object

def get_object_by_uid(uid):
    try:
        type, id = uid.split('#')
        type = int(type)
        id = int(id)
    except:
        raise exceptions.WrongUIDFormatError(uid=uid)

    return get_object(type, id)


def create_relation(relation, meta_object_1, meta_object_2):
    model = models.Relation.objects.create(relation=relation.TYPE,
                                           from_type=meta_object_1.TYPE,
                                           from_object=meta_object_1.id,
                                           to_type=meta_object_2.TYPE,
                                           to_object=meta_object_2.id)

    return relation(id=model.id,
                    object_1=meta_object_1,
                    object_2=meta_object_2)


def is_relation_exists(relation, meta_object_1, meta_object_2):
    return models.Relation.objects.filter(relation=relation.TYPE,
                                          from_type=meta_object_1.TYPE,
                                          from_object=meta_object_1.id,
                                          to_type=meta_object_2.TYPE,
                                          to_object=meta_object_2.id).exists()

def remove_relation(relation_id):
    models.Relation.objects.filter(id=relation_id).delete()


def create_relations_for_objects(relation, meta_object, connected_objects):
    for object in connected_objects:
        create_relation(relation, meta_object, object)


def remove_relations_from_object(relation, meta_object):
    models.Relation.objects.filter(relation=relation.TYPE, from_type=meta_object.TYPE, from_object=meta_object.id).delete()


def get_objects_related_from(meta_object, relation=None):
    query = models.Relation.objects.filter(from_type=meta_object.TYPE, from_object=meta_object.id)

    if relation:
        query = query.filter(relation=relation.TYPE)

    for relation_id, type_id, object_id in query.values_list('relation', 'to_type', 'to_object'):
        yield _RELATIONS[relation_id], get_object(type_id, object_id)


def get_objects_related_to(meta_object, relation=None):
    query = models.Relation.objects.filter(to_type=meta_object.TYPE, to_object=meta_object.id)

    if relation:
        query = query.filter(relation=relation.TYPE)

    for relation_id, type_id, object_id in query.values_list('relation', 'from_type', 'from_object'):
        yield _RELATIONS[relation_id], get_object(type_id, object_id)


def get_uids_related_from(meta_object, relation=None):
    query = models.Relation.objects.filter(from_type=meta_object.TYPE, from_object=meta_object.id)

    if relation:
        query = query.filter(relation=relation.TYPE)

    for type_id, object_id in query.values_list('to_type', 'to_object'):
        yield create_uid(type_id, object_id)


def get_uids_related_to(meta_object, relation=None):
    query = models.Relation.objects.filter(to_type=meta_object.TYPE, to_object=meta_object.id)

    if relation:
        query = query.filter(relation=relation.TYPE)

    for type_id, object_id in query.values_list('from_type', 'from_object'):
        yield create_uid(type_id, object_id)
