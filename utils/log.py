import logging
from typing import Callable

logging.basicConfig()


def named(_self, func: Callable):
    # BROKEN
    def name_it(msg: str):
        return f"[{_self}] {msg}"

    def _named(*args, **kwargs):
        if msg:= kwargs.get("msg", None):
            kwargs["msg"] = name_it(msg)
        else:
            args = list(args)
            args[1] = name_it(args[1])
        return func(*args, **kwargs)
    return _named


class Loggable:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.basicConfig(format='%(name)-12s: %(levelname)-8s %(message)s')
        self.logger = logging.getLogger()
        self.logger.setLevel("DEBUG")
        # self.logger._log = named(self, self.logger._log)

