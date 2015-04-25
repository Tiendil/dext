# coding: utf-8

import sys
import time
import Queue

from django.conf import settings as project_settings
from django.utils.log import getLogger
from django import db

from dext.common.amqp_queues import exceptions
from dext.common.amqp_queues.connection import connection

from dext.settings import settings


def run_with_newrelic(method, method_data):
    import newrelic.agent

    application = newrelic.agent.application()
    name = newrelic.agent.callable_name(method)

    with newrelic.agent.BackgroundTask(application, name):
        return method(**method_data)

_NEXT_WORKER_NUMBER = 0

class BaseWorker(object):
    STOP_SIGNAL_REQUIRED = True
    RECEIVE_ANSWERS = False
    LOGGER_PREFIX = None
    REFRESH_SETTINGS = True
    FULL_CMD_LOG = False
    GET_CMD_TIMEOUT = 9999999
    NO_CMD_TIMEOUT = 0

    @classmethod
    def get_next_number(cls):
        global _NEXT_WORKER_NUMBER
        _NEXT_WORKER_NUMBER += 1
        return _NEXT_WORKER_NUMBER

    def __init__(self, name, groups=None):
        self.name = name

        self.number = self.get_next_number()

        self.groups = set() if groups is None else set(groups)

        self.command_queue = connection.create_simple_buffer('%s_command' % self.name, no_ack=True)
        self.stop_queue = connection.create_simple_buffer('%s_stop' % self.name, no_ack=True) if self.STOP_SIGNAL_REQUIRED else None
        self.answers_queue = connection.create_simple_buffer('%s_answers' % self.name, no_ack=True) if self.RECEIVE_ANSWERS else None

        self.logger = getLogger('%s.%s' % (self.LOGGER_PREFIX, self.name))

        self.exception_raised = False
        self.stop_required = False
        self.initialized = False

        self.commands = {}

        self.prepair_commands_map()

    @property
    def pid(self): return self.name

    def run(self):
        while not self.exception_raised and not self.stop_required:
            try:
                db.reset_queries()

                if self.GET_CMD_TIMEOUT > 0:
                    cmd = self.command_queue.get(block=True, timeout=self.GET_CMD_TIMEOUT)
                else:
                    cmd = self.command_queue.get_nowait()

                if self.REFRESH_SETTINGS:
                    settings.refresh()
                self.process_cmd(cmd.payload)
            except Queue.Empty:
                if self.REFRESH_SETTINGS:
                    settings.refresh()
                self.process_no_cmd()
                if self.NO_CMD_TIMEOUT:
                    time.sleep(self.NO_CMD_TIMEOUT)

    def process_no_cmd(self):
        pass

    def close_queries(self):
        pass

    def clean_queues(self):
        self.command_queue.queue.purge()

    def prepair_commands_map(self):

        attributes = set(dir(self))

        for attribute in attributes:
            if attribute in ['process_cmd', 'cmd_answer', 'process_no_cmd']:
                continue

            if attribute.startswith('process_'):
                cmd_name = attribute[8:]
                if ('cmd_%s' % cmd_name) in attributes:
                    self.commands[cmd_name] = getattr(self, attribute)
                else:
                    raise exceptions.NoCmdMethodError(method=cmd_name)

            if attribute.startswith('cmd_'):
                cmd_name = attribute[4:]
                if ('process_%s' % cmd_name) not in attributes:
                    raise exceptions.NoProcessMethodError(method=cmd_name)


    def send_cmd(self, tp, data=None):
        self.command_queue.put({'type': tp, 'data': data if data else {}}, serializer='json', compression=None)


    def _prepair_cmd_data_for_log(self, data):
        if self.FULL_CMD_LOG:
            return data

        return {key: value for key, value in data.iteritems() if not isinstance(value, dict)}

    def process_cmd(self, cmd):
        cmd_type = cmd['type']
        cmd_data = cmd['data']

        self.logger.info('<%s> %r' % (cmd_type, self._prepair_cmd_data_for_log(cmd_data)))

        if not self.initialized and cmd_type != 'initialize':
            self.logger.error('ERROR: receive cmd before initialization')
            return

        try:
            cmd = self.commands[cmd_type]

            if project_settings.NEWRELIC_ENABLED:
                run_with_newrelic(cmd, cmd_data)
            else:
                cmd(**cmd_data)
        except Exception: # pylint: disable=W0703
            self.exception_raised = True
            self.logger.error('Exception in worker "%r"' % self,
                              exc_info=sys.exc_info(),
                              extra={} )

    def wait_answers_from(self, code, workers=(), timeout=60.0):

        while workers:

            try:
                answer_cmd = self.answers_queue.get(block=True, timeout=timeout)
                # answer_cmd.ack()
            except Queue.Empty:
                raise exceptions.WaitAnswerTimeoutError(code=code, workers=workers, timeout=timeout)

            cmd = answer_cmd.payload

            if cmd['code'] == code:
                worker_id = cmd['worker']
                if worker_id in workers:
                    workers.remove(worker_id)
                else:
                    raise exceptions.UnexpectedAnswerError(cmd=cmd)
            else:
                raise exceptions.WrongAnswerError(cmd=cmd, workers=workers)

    def cmd_answer(self, code, worker):
        self.answers_queue.put({'code': code, 'worker': worker}, serializer='json', compression=None)
