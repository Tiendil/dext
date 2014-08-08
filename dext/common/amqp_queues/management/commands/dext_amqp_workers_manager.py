# coding: utf-8
import os
import time
import subprocess
import optparse

from django.core.management.base import BaseCommand
from django.conf import settings as project_settings

from dext.common.utils import pid

from dext.common.amqp_queues.conf import amqp_settings
from dext.common.amqp_queues import environment


class Command(BaseCommand):

    help = 'manage amqp workers'

    requires_model_validation = False

    option_list = BaseCommand.option_list + ( optparse.make_option('-c', '--command',
                                                                   action='store',
                                                                   type=str,
                                                                   dest='command',
                                                                   help='start|stop|restart|status'),
                                              optparse.make_option('-g', '--group',
                                                                   action='store',
                                                                   type=str,
                                                                   dest='group',
                                                                   help='name of workers group'), )

    def start(self):
        for worker in self.workers:
            worker.clean_queues()

        for worker in self.workers:
            print 'start %s' % worker.name
            with open(os.devnull, 'w') as devnull:
                subprocess.Popen(['django-admin.py', 'dext_amqp_worker', '-w', worker.name, '--settings', '%s.settings' % project_settings.PROJECT_MODULE],
                                 stdin=devnull, stdout=devnull, stderr=devnull)


    def stop(self):
        for worker in reversed(self.workers):

            if worker.STOP_SIGNAL_REQUIRED and pid.check(worker.pid):
                print '%s found, send stop command' % worker.name
                worker.cmd_stop()
                print 'waiting answer'
                worker.stop_queue.get(block=True)
                print 'answer received'

        while any(pid.check(worker.pid) for worker in self.workers):
            time.sleep(0.1)


    def force_stop(self):
        for worker in reversed(self.workers):
            print 'force stop %s' % worker.name
            pid.force_kill(worker.name)

    def before_start(self): pass
    def before_stop(self): pass
    def before_force_stop(self): pass

    def after_start(self): pass
    def after_stop(self): pass
    def after_force_stop(self): pass

    @pid.protector(amqp_settings.WORKERS_MANAGER_PID)
    def handle(self, *args, **options):

        command = options['command']

        group = options['group']

        env = environment.get_environment()

        self.workers = sorted([worker for worker in env.workers if group in worker.groups], key=lambda w: w.number)

        if command == 'start':
            self.before_start()
            self.start()
            self.after_start()
            print 'infrastructure started'

        elif command == 'stop':
            self.before_stop()
            self.stop()
            self.after_stop()
            print 'infrastructure stopped'

        elif command == 'force_stop':
            self.before_force_stop()
            self.force_stop()
            self.after_force_stop()
            print 'infrastructure stopped (force)'

        elif command == 'restart':
            self.before_stop()
            self.stop()
            self.after_stop()

            self.before_start()
            self.start()
            self.after_start()
            print 'infrastructure restarted'

        elif command == 'status':
            print 'command "%s" does not implemented yet ' % command

        else:
            print 'command did not specified'
