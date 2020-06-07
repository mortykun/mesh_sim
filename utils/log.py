import logging

logging.basicConfig()


class Loggable:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.basicConfig(format='%(name)-12s: %(levelname)-8s %(message)s')
        self.logger = logging.getLogger()
        self.logger.setLevel("DEBUG")
