import logging

logging.basicConfig()


class Loggable:

    def __init__(self):
        logging.basicConfig()
        self.logger = logging.getLogger()
