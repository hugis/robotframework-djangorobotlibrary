import os
import sys
from pathlib import Path

import django
from django.conf import settings
from django.core.management import call_command
from django.db import connections

# noinspection PyProtectedMember
from django.test.testcases import (
    LiveServerThread,
    _StaticFilesHandler,
    _TransactionTestCaseDatabasesDescriptor,
)
from django.test.utils import modify_settings
from django.urls import reverse
from django.utils.module_loading import import_string

from robot.api import logger


__version__ = "19.1a0"


class DjangoRobotLibrary:
    """DjangoRobotLibrary is a web testing library to test Django with Robot
    Framework.
    """

    server_thread_class = LiveServerThread
    static_handler = _StaticFilesHandler
    databases = _TransactionTestCaseDatabasesDescriptor()

    def __init__(self, django_project_path, django_settings, host="localhost", port=0):
        django_project_path = Path(django_project_path).resolve()
        sys.path.append(str(django_project_path))

        self.django_settings = django_settings
        self.host = host
        self.port = port
        self.server_thread = None
        self._live_server_modified_settings = None
        self._setup_django()

    def _setup_django(self):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", self.django_settings)
        django.setup()

    @classmethod
    def _databases_names(cls, include_mirrors=True):
        # Only consider allowed database aliases, including mirrors or not.
        # Snipped copied from: https://github.com/django/django/blob/master/django/test/testcases.py
        return [
            alias
            for alias in connections
            if alias in cls.databases
            and (
                include_mirrors
                or not connections[alias].settings_dict["TEST"]["MIRROR"]
            )
        ]

    def start_live_django_server(self):
        connections_override = {}

        for conn in connections.all():
            # If using in-memory sqlite databases, pass the connections to
            # the server thread.
            if conn.vendor == "sqlite" and conn.is_in_memory_db():
                # Explicitly enable thread-shareability for this connection
                conn.inc_thread_sharing()
                connections_override[conn.alias] = conn

        liveserver_kwargs = {
            "port": self.port,
            "connections_override": connections_override,
        }

        if "django.contrib.staticfiles" in settings.INSTALLED_APPS:
            from django.contrib.staticfiles.handlers import StaticFilesHandler

            liveserver_kwargs["static_handler"] = StaticFilesHandler
        else:
            liveserver_kwargs["static_handler"] = self.static_handler

        self._live_server_modified_settings = modify_settings(
            ALLOWED_HOSTS={"append": self.host}
        )

        self.server_thread = self.server_thread_class(self.host, **liveserver_kwargs)

        self.server_thread.daemon = True
        self.server_thread.start()
        self.server_thread.is_ready.wait()

        if self.server_thread.error:
            raise self.server_thread.error

        logger.console(
            f"Start Django on {self.server_thread.host}:{self.server_thread.port}"
        )

        return self.server_thread

    def stop_live_django_server(self):
        self.server_thread.terminate()
        self.server_thread.join()
        logger.console("Stop Django live server")

    def load_fixtures(self, fixtures):
        if not isinstance(fixtures, list) or not isinstance(fixtures, tuple):
            fixtures = [fixtures]

        for db_name in self._databases_names(include_mirrors=False):
            call_command("loaddata", *fixtures, **{"verbosity": 0, "database": db_name})

    @staticmethod
    def reverse_to_url(view_name, *args, **kwargs):
        return reverse(view_name, args=args, kwargs=kwargs)

    @staticmethod
    def create_with_factory_boy(factory, **kwargs):
        factory_class = import_string(factory)
        model = factory_class(**kwargs)
        return model

    @staticmethod
    def get_model_manager(model, manager=None):
        model_class = import_string(model)
        if manager is None:
            # noinspection PyProtectedMember
            return model_class._default_manager
        else:
            if hasattr(model_class, manager):
                return getattr(model_class, manager)
            else:
                raise AttributeError
