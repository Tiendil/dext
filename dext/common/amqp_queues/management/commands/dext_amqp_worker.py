# coding: utf-8
import sys
import traceback
import optparse

from django.core.management.base import BaseCommand
from django.conf import settings as project_settings

from dext.common.utils import pid

from dext.common.amqp_queues import environment


def initialize_newrelic():
    import newrelic.agent
    newrelic.agent.initialize(project_settings.NEWRELIC_CONF_PATH)


class Command(BaseCommand):

    help = 'run specified workers'

    option_list = BaseCommand.option_list + ( optparse.make_option('-w', '--worker',
                                                                   action='store',
                                                                   type=str,
                                                                   dest='worker',
                                                                   help='worker name'), )

    requires_model_validation = False

    def handle(self, *args, **options):

        worker_name = options['worker']

        env = environment.get_environment()

        worker = env.workers.get_by_name(worker_name)

        handler = pid.protector(worker.pid)(self._handle)

        handler(worker)


    def _handle(self, worker):
        try:
            worker.initialize()

            if project_settings.NEWRELIC_ENABLED:
                initialize_newrelic()

            worker.run()

        except KeyboardInterrupt:
            pass
        except Exception:
            traceback.print_exc()
            worker.logger.error('Infrastructure worker exception: %s' % worker.name,
                                exc_info=sys.exc_info(),
                                extra={} )

        # TODO: close worker's queues
