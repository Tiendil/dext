# coding: utf-8

from dext.common.utils import exceptions

class MetaRelationsError(exceptions.DextError):
    MSG = None


class DuplicateRelationError(MetaRelationsError):
    MSG = 'relation with such TYPE has been registered already: %(type)s'

class DuplicateTypeError(MetaRelationsError):
    MSG = 'type with such TYPE has been registered already: %(type)s'


class WrongTypeError(MetaRelationsError):
    MSG = 'type with such TYPE has not been registered: %(type)s'

class WrongObjectError(MetaRelationsError):
    MSG = 'object %(object)s of type %(type)s is not exist'

class WrongUIDFormatError(MetaRelationsError):
    MSG = 'wrong uid format: %(uid)s'
