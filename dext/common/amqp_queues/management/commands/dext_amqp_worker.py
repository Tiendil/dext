# coding: utf-8
import sys
import signal
import traceback

from django.core.management.base import BaseCommand
from django.conf import settings as project_settings

from dext.common.amqp_queues import environment


class Command(BaseCommand):

    help = 'run specified workers'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('-w', '--worker', action='store', type=str, dest='worker', help='worker name')

    requires_model_validation = False

    def handle(self, *args, **options):

        worker_name = options['worker']

        env = environment.get_environment()

        worker = env.workers.get_by_name(worker_name)

        if worker is None:
            raise Exception('Worker {name} has not found'.format(name=worker_name))

        self._handle(worker)


    def _handle(self, worker):
        try:
            signal.signal(signal.SIGTERM, worker.on_sigterm)

            if worker.initialize() is False:
                worker.logger.info('worker stopped due method initilize return False')
                return

            worker.run()

            worker.logger.info('worker stopped')

        except KeyboardInterrupt:
            pass
        except Exception:
            traceback.print_exc()
            if worker and worker.logger:
                worker.logger.error('Infrastructure worker exception: %s' % worker.name,
                                    exc_info=sys.exc_info(),
                                    extra={} )

        # TODO: close worker's queues
