import logging

"""
@author Ilan Beer, Chris Pang
"""


class CustomColorFormatter(logging.Formatter):
    """
    Used to add color to logs appearing in console.
    """

    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset,
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class LoggerUtil:
    # Class variables, NOT instance variables
    has_initialized = False
    default_fmt = "%(asctime)s | %(levelname)8s | %(name)s | %(message)s"
    default_log_level = logging.INFO

    def __init__(self, name, log_level=None, log_file=None):
        if not LoggerUtil.has_initialized:
            LoggerUtil.initialize()

        self.logger = logging.getLogger(name)

        if log_level is not None:
            if log_level == "DEBUG":
                level = logging.DEBUG
            elif log_level == "INFO":
                level = logging.INFO
            elif log_level == "WARNING":
                level = logging.WARNING
            elif log_level == "ERROR":
                level = logging.ERROR
            elif log_level == "CRITICAL":
                level = logging.CRITICAL
            else:
                raise Exception(
                    f"log_level {log_level} is not valid. Please use DEBUG, INFO, WARNING, ERROR, or CRITICAL."
                )
        else:
            level = LoggerUtil.default_log_level

        self.logger.setLevel(level)

        if log_file is not None:
            # Create file handler for logging to a file
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(logging.Formatter(LoggerUtil.default_fmt))
            self.logger.addHandler(file_handler)

    @classmethod
    def initialize(cls):
        """
        This should be run only ONCE on a class-level,
        when we want to initialize/overwrite the root logger.
        Subsequent instances of LoggerUtil will not call this.
        """
        # print('Initializing root logger')
        logging.basicConfig(
            level=LoggerUtil.default_log_level,
            format=LoggerUtil.default_fmt,
            force=True,
        )
        root_logger = logging.getLogger()
        LoggerUtil.set_logger_formatter(root_logger)
        LoggerUtil.has_initialized = True

    @classmethod
    def set_logger_formatter(cls, logger):
        if logger.hasHandlers():
            # print('Logger has handlers')
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    # print(f'Setting StreamHandler {handler} to use our CustomColorFormatter')
                    handler.setFormatter(CustomColorFormatter(LoggerUtil.default_fmt))
                else:
                    # print(f'Setting handler {handler} to use our Formatter')
                    handler.setFormatter(logging.Formatter(LoggerUtil.default_fmt))

    @classmethod
    def format_uvicorn(cls):
        logger_names = ["uvicorn", "uvicorn.access", "uvicorn.error"]
        for logger_name in logger_names:
            logger = logging.getLogger(logger_name)
            LoggerUtil.set_logger_formatter(logger)

    def debug(
        self, text, *args, exc_info=None, stack_info=False, stacklevel=1, extra=None
    ):
        self.logger.debug(
            text,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
        )

    def info(
        self, text, *args, exc_info=None, stack_info=False, stacklevel=1, extra=None
    ):
        self.logger.info(
            text,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
        )

    def warning(
        self, text, *args, exc_info=None, stack_info=False, stacklevel=1, extra=None
    ):
        self.logger.warning(
            text,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
        )

    def error(
        self, text, *args, exc_info=None, stack_info=False, stacklevel=1, extra=None
    ):
        self.logger.error(
            text,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
        )

    def critical(
        self, text, *args, exc_info=None, stack_info=False, stacklevel=1, extra=None
    ):
        self.logger.critical(
            text,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
        )

    def exception(
        self, text, *args, exc_info=True, stack_info=False, stacklevel=1, extra=None
    ):
        self.logger.exception(
            text,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
        )
