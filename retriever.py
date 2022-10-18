from genericpath import isfile
from os import path
import sys

from configuration import config
from flask import Flask
import logging
from logging.handlers import RotatingFileHandler
from typing import Tuple, List


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


class Retriever:
    _input_file = None;
    _output_file = None;
    _app = None
    _allowed_input_values = [
        {
            "value": config.MANDATORY_PARAMETER_INPUT,
            "description": "Input file/folder",
            "is_optional": False
        },
        {
            "value": "--output",
            "description": "Output file",
            "is_optional": False
        },
        {
            "value": "--mfip",
            "description": "Most frequent IP",
            "is_optional": True
        },
        {
            "value": "--lfip",
            "description": "Least frequent IP",
            "is_optional": True
        },
        {
            "value": "--eps",
            "description": "Events per second",
            "is_optional": True
        },
        {
            "value": "--bytes",
            "description": "Total amount of bytes exchanged",
            "is_optional": True
        }
    ]

    def constructor(self, 
        app:Flask,
        input_file:str,
        output_file:str):

        self._app = app
        self._input_file = input_file
        self._output_file = output_file

    @staticmethod
    def help(command: str, msg: str) -> None:
        if command == "help" or command == "?" or command == "-h" or command == "-help":
            input_tip = "/path/to/input/file/or/folder"
            output_tip = "/path/to/output/file"
            print("Log retriever 1.0")
            if msg != "":
                print(f">>Execution Error: {msg}\n")

            print(f"To run retriever:\n\tpython retriever.py --input={input_tip} --output={output_tip}")
            print("\nOperations")
            print("\n".join(f"{item['value']}\t\t{item['description']}" for item in Retriever._allowed_input_values))

            if msg != "":
                sys.exit(1)
            
            sys.exit(0)

    @staticmethod
    def validate_arguments(args:List[str])-> Tuple[bool, str, str, List[str]]:
        is_valid = False
        input = None
        output = None
        options = []
        msg = ""
        """ Arguments might come in any order """
        if len(args) >= 3:
            input = {"path": None, "is_a_folder": True}

            for index in range(len(args)):
                """ First value is always the script name """
                if index == 0:
                    continue

                argument = args[index].split(config.INPUT_VALID_ASIIGNER)[0]

                if argument.lower() == config.MANDATORY_PARAMETER_INPUT:
                    try:
                        input_path = args[index].split(config.INPUT_VALID_ASIIGNER)[1]
                        if not path.exists(input_path):
                            msg = "--input path doesn't exist"
                            return is_valid, input, output, options, msg
                        
                        input["path"] = input_path
                        input["is_a_folder"] = path.isdir(input_path)
                    except:
                        msg = "Use '=' to asign a path to --input value"
                        return is_valid, input, output, options, msg
                
                if argument.lower() == config.MANDATORY_PARAMETER_OUTPUT:
                    try:
                        output_path = args[index].split(config.INPUT_VALID_ASIIGNER)[1]
                        if path.isdir(output_path):
                            msg = "--output path is a dir and should be a file"
                            return is_valid, input, output, options, msg
                        
                        output = output_path
                    except:
                        msg = "Use '=' to asign a path to --output value"
                        return is_valid, input, output, options, msg

                """" Evaluation optional parameters """
                if argument.lower() not in [config.MANDATORY_PARAMETER_INPUT, config.MANDATORY_PARAMETER_OUTPUT]:
                    optional_param = list(filter(lambda x: x['value'] == argument, Retriever._allowed_input_values))

                    if len(optional_param) == 0:
                        msg += f"\n>>{argument} argument is not recognized"


            is_valid = input["path"] is not None and output is not None

            msg += "\n>>--input argument is missging" if input["path"] is None else ""
            msg += "\n>>--output argument is missging" if output is None else ""

        return is_valid, input, output, options, msg

def main(name):

    app = Flask(name)
    args = sys.argv

    if args:
        valid_args, input, output, options, msg = Retriever.validate_arguments(args)

        if not valid_args:
            Retriever.help(command="help", msg=msg)

        logger(app)


if __name__ == '__main__':
    main(__name__)
