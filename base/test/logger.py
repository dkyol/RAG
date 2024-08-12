import argparse
from dp_solutions_architecture_utils.logger import LoggerUtil


def main(arg):
    # Each LoggerUtil should be instantiated by passing in __name__
    logger = LoggerUtil(__name__,
                        log_level=arg.log,
                        log_file=arg.file)
    logger.debug(arg)
    logger.debug("Sample debug message")
    logger.info("Sample info message")
    logger.warning("Sample warning message")
    logger.error("Sample error message")
    logger.critical("Sample critical message")

    logger2 = LoggerUtil('logger2',
                        log_level=arg.log,
                        log_file=arg.file)
    logger2.info("Now using Logger 2")

    logger2.debug(arg.string)
    logger2.info(arg.string)
    logger2.warning(arg.string)
    logger2.error(arg.string)
    logger2.critical(arg.string)


if __name__ == '__main__':
    args = argparse.ArgumentParser(description='python app')
    args.add_argument('-l', '--log', default="ERROR",
                      type=str, help='for log level')

    args.add_argument('-f', '--file', default=None, type=str,
                      help='the log file name that we write to')

    args.add_argument('-s', '--string', default="Testing the logger", type=str,
                      help='the string to log')

    parsed_args = args.parse_args()

    main(parsed_args)
