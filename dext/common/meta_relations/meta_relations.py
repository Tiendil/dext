# coding: utf-8

from . import objects


class TestType_1(objects.MetaType):
    TYPE = -1

    @classmethod
    def create_from_id(cls, id): return cls(id=id) if id >= 0 else None


class TestType_2(objects.MetaType):
    TYPE = -2

    @classmethod
    def create_from_id(cls, id): return cls(id) if id >= 0 else None


class TestRelation_1(objects.MetaRelation):
    TYPE = -1


class TestRelation_2(objects.MetaRelation):
    TYPE = -2
