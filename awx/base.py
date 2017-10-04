"""Awx base module."""
import inspect
from logging import DEBUG, INFO
from logging import Formatter, getLogger, StreamHandler

from tower_cli import get_resource


class LoggerMixin(object):
    """A logger mixin class."""

    @classmethod
    def create_logger(cls, name, verbose):
        """Create logger.

        :param name: Logger name.
        :type name: str
        :param verbose: Verbosity level.
        :type verbose: int
        """
        # get logger
        logger = getLogger(name)

        # skip creating logger if handler exists
        if logger.handlers.__len__() > 0:
            return

        # determine log formatting
        if verbose >= 1:
            log_level = DEBUG
            console = ("%(asctime)s %(levelname)s "
                       "[%(name)s.%(funcName)s:%(lineno)d] %(message)s")
        else:
            log_level = INFO
            console = ("%(asctime)s %(levelname)s "
                       "[%(name)s.%(funcName)s:%(lineno)d] %(message)s")

        # create stream handler
        handler = StreamHandler()

        # configure handler
        handler.setLevel(log_level)
        handler.setFormatter(Formatter(console, datefmt='%Y-%m-%d %H:%M:%S'))

        # configure logger
        logger.setLevel(log_level)
        logger.addHandler(handler)

    @property
    def logger(self):
        """Return logger."""
        return getLogger(inspect.getmodule(inspect.stack()[1][0]).__name__)


class AwxBase(LoggerMixin):
    """Awx base class."""
    __resource_name__ = None

    @property
    def name(self):
        """Return resource name."""
        return self.__resource_name__

    @property
    def resource(self):
        """Return resource class object."""
        return get_resource(self.name)
