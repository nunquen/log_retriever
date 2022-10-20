import os
import sys

from configuration import config
from datetime import datetime
from flask import Flask
from libs import utils
import logging
from logging.handlers import RotatingFileHandler
import pandas as pd
from typing import Dict, List, Tuple

sys.path.append('../')

def logger(app):
    """ Log handler """
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
    _app = None
    _input_file = None
    _output_file = None
    _opeartions = []
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
    _csv_columns = [
        "timestamp",
        "response_header_size",
        "client_ip",
        "http_response_code",
        "response_size",
        "http_request_method",
        "url",
        "username",
        "access_type_and_destination_ip", #This filed will be splitted by "/" into 2 fields
        "respopnse_type"
    ]
    _df = None #Pandas DataFrame
    _output_data = [{"operation": "result"}] #all activated operations will post their results here
    _processed_files = 0

    def __init__(self, 
        app:Flask,
        input_file:str,
        output_file:str,
        opeartions:List[Dict]):

        self._app = app
        self._input_file = input_file
        self._output_file = output_file
        self._opeartions = opeartions
        self._df = pd.DataFrame()

    @staticmethod
    def help(command: str, msg: str) -> None:
        """ Help menu """
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
        """ Arguments validation (they might come in any order) """
        is_valid = False
        input = None
        output = None
        opeartions = []
        msg = ""
        
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
                        if not os.path.exists(input_path):
                            msg = "--input path doesn't exist"
                            return is_valid, input, output, opeartions, msg
                        
                        input["path"] = input_path
                        input["is_a_folder"] = os.path.isdir(input_path)
                    except:
                        msg = "Use '=' to asign a path to --input value"
                        return is_valid, input, output, opeartions, msg
                
                if argument.lower() == config.MANDATORY_PARAMETER_OUTPUT:
                    try:
                        output_path = args[index].split(config.INPUT_VALID_ASIIGNER)[1]
                        if os.path.isdir(output_path):
                            msg = "--output path is a dir and should be a file"
                            return is_valid, input, output, opeartions, msg
                        
                        output = output_path
                    except:
                        msg = "Use '=' to asign a path to --output value"
                        return is_valid, input, output, opeartions, msg

                """" Evaluation optional parameters """
                if argument.lower() not in [config.MANDATORY_PARAMETER_INPUT, config.MANDATORY_PARAMETER_OUTPUT]:
                    optional_param = list(filter(lambda x: x['value'] == argument, Retriever._allowed_input_values))

                    if len(optional_param) == 0:
                        msg += f"\n>>{argument} argument is not recognized"
                        continue
                    
                    opeartions.extend(optional_param)


            is_valid = input["path"] is not None and output is not None

            msg += "\n>>--input argument is missging" if input["path"] is None else ""
            msg += "\n>>--output argument is missging" if output is None else ""

        return is_valid, input, output, opeartions, msg

    def read_input(self, input_file:Dict)-> None:
        """ Read input files (one or many) and create a Pandas DataFrame """
        file_list = []
        input_dataframe = []
        # Read single file or many files and have them into the file_list 
        if not input_file["is_a_folder"]:
            self._app.logger.info("READING SINGLE INPUT FILE")
            file_list.append(input_file["path"])
        else:
            self._app.logger.info(f"READING INPUT FILES FROM FOLDER: {len(os.listdir(input_file['path']))} files.")
            for file in os.listdir(input_file["path"]):
                file_list.append(f"{input_file['path']}{os.path.sep}{file}")

        # Saving for statistics
        self._processed_files = len(file_list)

        # Every read will create a dataframe that will be attached to the class dataframe
        for file in file_list:
            df = utils.read_csv_file(
                csv_file=file,
                columns=self._csv_columns,
                has_header=None,
                field_separators=r"\s+"
            )
            input_dataframe.append(df)
        
        self._df = pd.concat(input_dataframe)
        # Splitting access_type_and_destination_ip into two columns: access_type, destination_ip
        df_temp = pd.DataFrame()
        df_temp[['access_type','destination_ip']] = self._df['access_type_and_destination_ip']\
            .str.split('/',expand=True)
        self._df["access_type"] = df_temp["access_type"]
        self._df["destination_ip"] = df_temp["destination_ip"]
        # Dropping un wanted columns
        self._df = self._df.drop("access_type_and_destination_ip", axis='columns')
        # Timestamp to date
        self._df['timestamp_in_seconds'] = self._df['timestamp'].apply(
            lambda x: datetime.fromtimestamp(x).isoformat(timespec='seconds'))
        # Sorting by timestamp
        self._df.sort_values(by=['timestamp'], inplace=True)


    def apply_operations(self)-> List:
        """ Applying custom operations for statistics """
        result = []

        if self._df.shape[0] == 0:
            return
        
        for index in range(len(self._opeartions)):
            operation = self._opeartions[index]
            out = {"description": "", "result": ""}
            out["description"] = operation["description"]

            if operation["value"] == "--mfip":
                """ Most frequent IP """
                client_ip_df = self._df.groupby(["client_ip"]).count()["timestamp_in_seconds"]
                client_ip = client_ip_df.idxmax()
                client_ip_times = client_ip_df.max()

                destination_ip_df = self._df.groupby(["destination_ip"]).count()["timestamp_in_seconds"]
                destination_ip = destination_ip_df.idxmax()
                destination_ip_times = destination_ip_df.max()

                out["result"] = f"Client IP '{client_ip}' appears {client_ip_times} times"
                out["result"] += f" and Destination IP '{destination_ip}' appears {destination_ip_times} times"

            if operation["value"] == "--lfip":
                """ Less frequent IP """
                client_ip_df = self._df.groupby(["client_ip"]).count()["timestamp_in_seconds"]
                client_ip = client_ip_df.idxmin()
                client_ip_times = client_ip_df.min()

                destination_ip_df = self._df.groupby(["destination_ip"]).count()["timestamp_in_seconds"]
                destination_ip = destination_ip_df.idxmin()
                destination_ip_times = destination_ip_df.min()

                out["result"] = f"Client IP '{client_ip}' appears {client_ip_times} times"
                out["result"] += f" and Destination IP '{destination_ip}' appears {destination_ip_times} times"


            if operation["value"] == "--eps":
                """" Events Per Second """
                eps_value = self._df.groupby(['timestamp_in_seconds'])['timestamp_in_seconds'].count().mean()
                out["result"] = eps_value

            if operation["value"] == "--bytes":
                """ Total amount of bytes exchanged """
                response_header_size_value = self._df["response_header_size"].sum()
                response_size_value = self._df["response_size"].sum()
                bytes = response_header_size_value + response_size_value
                size, format = utils.bytes_formatter(bytes)
                out["result"] = f"{round(size, 2)}{format} in total ({bytes} bytes)"

            result.append(out)

        return result
        
    def print_output(self, data: List[Dict]):

        statistics_data = {
            "application_name": config.APP_NAME,
            "processed_files": self._processed_files,
            "operations": data
        }

        utils.write_json_file(output_path=self._output_file, data=statistics_data)

def main(name):

    app = Flask(name)
    args = sys.argv

    if args:
        valid_args, input, output, opeartions, msg = Retriever.validate_arguments(args)

        if not valid_args:
            Retriever.help(command="help", msg=msg)

        logger(app)

        retriever = Retriever(
            app=app,
            input_file=input,
            output_file=output,
            opeartions=opeartions
        )

        retriever.read_input(input_file=input)

        operations = retriever.apply_operations()

        retriever.print_output(data=operations)

        #TODO:
        # Generate csv output file 
        # Move processed files will temp/done/retrieved_YYYYMMDDHHMMSS folder



if __name__ == '__main__':
    main(__name__)
