"""
        Loads environment specific configuration from a configuration file stored in
        a top-level deployment directory.

        web2py/
                deployment/
                        (application name).cfg
                        environment.txt  # Not checked in.  We will manually put this on all our servers based upon where code is running
"""

import logging
import os.path
import ConfigParser


DEPLOYMENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../deployment"))
ENVIRONMENT_TXT = os.path.join(DEPLOYMENT_DIR, "environment.txt")


class Config(object):

    def __init__(self, filename):
        self.log = logging.getLogger(__name__)
        self.environment = "local"

        try:
            with open(ENVIRONMENT_TXT, "rb") as f:
                self.environment = f.read().strip()
        except IOError:
            self.log.warn("Unable to read environment file '%s'.  Assuming %s environment.", ENVIRONMENT_TXT, self.environment)

        self.config = ConfigParser.SafeConfigParser()
        try:
            with open(filename, "r") as f:
                self.config.read(f)
        except IOError:
            self.log.exception("Unable to read platform configuration file: %s", filename)
            raise

        self.config.read(filename)
        if self.environment not in self.config.sections():
            raise Exception("Configuration settings for {env} are not defined in {file}.".format(env=self.environment, file=filename))

    def __getattr__(self, name):
        return self._config(name)

    def _has_option(self, name):
        return self.config.has_option(self.environment, name)

    def _config(self, name):
        return self.config.get(self.environment, name)

    def _config_boolean(self, name):
        return self.config.getboolean(self.environment, name)

    @property
    def db_migrate_enabled(self):
        return self._config_boolean("db_migrate_enabled")

    def db_url(self):
        return "mysql://{user}:{password}@{host}/{database}".format(
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                database=self.db_name
        )