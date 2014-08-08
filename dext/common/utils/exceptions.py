# coding: utf-8

class DextError(Exception):
    MSG = None

    def __init__(self, **kwargs):
        super(DextError, self).__init__(self.MSG % kwargs)
