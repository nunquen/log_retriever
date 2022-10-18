import sys
from flask import Flask
import logging
from logging.handlers import RotatingFileHandler

from configuration import config

sys.path.append('../')


def logger(app):

    logHandler = RotatingFileHandler(filename=config.LOG_PATH + config.LOG_NAME,
                                        maxBytes=config.LOG_MAXBYTES,
                                        backupCount=config.LOG_BACKUPCOUNT)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    logHandler.setFormatter(formatter)

    # set the log handler level
    logHandler.setLevel(logging.INFO)

    # set the app logger level
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(logHandler)
    app.logger.info("Starting logger")


def main(name):

    app = Flask(name)
    logger(app)
    args = sys.argv

    if args:
        if len(args) > 1:
            command = args[1]

            if command == "help" or command == "?" or command == "-h" or command == "-help":
                app.logger.info("Log retriever 1.0")
                app.logger.info("Execution example: retriever ")
                sys.exit(0)


if __name__ == '__main__':
    main(__name__)
