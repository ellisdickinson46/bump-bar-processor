import sys
from logbook import Logger, StreamHandler, Processor


def create_logger(log_name: str, log_level: str) -> Logger:
    """Create a logger instance with automatic class name injection at call site"""
    format_string = '[{record.time:%Y-%m-%d %H:%M:%S.%f}] {record.level_name:<8} : [{record.extra[class]}::{record.func_name}] {record.message}'
    logger = Logger(log_name)

    def inject_true_calling_class(record):
        frame = record.frame
        class_name = 'N/A'

        while frame:
            if (local_self := frame.f_locals.get('self')):
                if (class_name := local_self.__class__.__name__) not in ('Logger', ):
                    break
            frame = frame.f_back

        record.extra['class'] = class_name

    if sys.stdout:
        streamhandler = StreamHandler(
            sys.stdout,
            level=log_level,
            bubble=True,
            format_string=format_string
        )
        logger.handlers.append(streamhandler)

    Processor(inject_true_calling_class).push_application()
    return logger
