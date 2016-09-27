# coding: utf-8

from dext.common.utils import exceptions

class AmqpQueuesError(exceptions.DextError):
    MSG = None


class UnexpectedAnswerError(AmqpQueuesError):
    MSG = 'unexpected unswer from worker: %(cmd)r'


class WrongAnswerError(AmqpQueuesError):
    MSG = 'wrong answer: %(cmd)r, expected answers from %(workers)r'


class WaitAnswerTimeoutError(AmqpQueuesError):
    MSG = 'timeout (%(timeout)f sec) while waiting answer code "%(code)s" from workers %(workers)r'


class NoCmdMethodError(AmqpQueuesError):
    MSG = 'method "%(method)s" specified without appropriate cmd_* method'

class NoProcessMethodError(AmqpQueuesError):
    MSG = 'method "%(method)s" specified without appropriate process_* method'
