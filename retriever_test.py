from datetime import datetime
from libs import utils
from flask import Flask
import pandas as pd
from retriever import Retriever
import unittest

class RetrieverTest(unittest.TestCase):
    _app = None
    _retriever = None

    def __init__(self, methodName: str = ...) -> None:
        self._app = Flask("__name__")
        self._retriever = Retriever(
            app=self._app,
            input_file="../tmp/input",
            output_file="../tmp/output/output.json",
            operations=[]
        )
        super().__init__(methodName)

    def get_dataframe(df:pd.DataFrame):
        data = {
            "timestamp": [
                1157689312, 1157689320, 1157689320, 1157689321, 1157689322,
                1157689323, 1157689324, 1157689324, 1157689324, 1157689325
            ],
            "response_header_size": [
                5006, 2864, 1357, 1, 1464, 
                3856, 1372, 1457, 1465, 1452
            ],
            "client_ip": [
                "10.105.21.190", "10.105.21.191", "10.105.21.191", "10.105.21.193", "10.105.21.193",
                "10.105.21.193", "10.105.21.194", "10.105.21.194", "10.105.21.194", "10.105.21.194"
            ],
            "http_response_code": [
                "TCP_MISS/200", "TCP_MISS/200", "TCP_MISS/200", "TCP_MISS/200", "TCP_MISS/200",
                "TCP_MISS/200", "TCP_MISS/200", "TCP_MISS/200", "TCP_MISS/200", "TCP_MISS/200"
            ],
            "response_size": [
                19763, 10182, 214, 1464, 5625,
                30169, 399, 215, 215, 214
            ],
            "http_request_method": [
                "CONNECT", "GET", "GET", "GET", "GET",
                "GET", "GET", "GET", "GET", "GET"
            ],
            "url": [
                "https://www.swissre.com/","http://finance.yahoo.com/", "http://www.goonernews.com/",
                "https://intranet.swissre.com/","http://www.github.com/", "http://www.twitter.com/",
                "http://www.bbc.com/","http://www.swissre.com/", "http://www.swissre.com/",
                "http://www.swissre.com/"
            ],
            "username": [
                "smaldonado", "tszivos", "mszczur", "dredondo", "umaurer",
                "ssommaruga", "aberset", "jfurrer", "uochsenbein", "jmuzinger"
            ],
            "access_type": [
                "DIRECT", "DIRECT", "DIRECT", "DIRECT", "DIRECT",
                "DIRECT", "DIRECT", "DIRECT", "DIRECT", "DIRECT"
            ],
            "destination_ip": [
                "209.73.177.115", "207.58.145.61", "207.58.145.61", "-", "-",
                "-", "207.58.145.61", "207.58.145.61", "207.58.145.61", "207.58.145.61"
            ], 
            "respopnse_type": [
                "-", "-", "text/html", "text/css", "text/javascript",
                "image/gift", "text/html", "-", "-", "text/html"
            ]
        }

        df = pd.DataFrame(data)
        df['timestamp_in_seconds'] = df['timestamp'].apply(
            lambda x: datetime.fromtimestamp(x).isoformat(timespec='seconds'))
        # Sorting by timestamp
        df.sort_values(by=['timestamp'], inplace=True)
        return df

    def test_arguments_no_input_file(self):
        args = [
            "retriever.py",
            "--output=tmp/output/output.json",
            "--mfip",
            "--lfip",
            "--eps",
            "--bytes"
        ]

        #with mock.patch(
        #    "retriever.Retriever.validate_arguments"
        #) as validate_arguments_mock:
        valid_args, _, _, _, msg = Retriever.validate_arguments(args)
        self.assertFalse(valid_args)
        self.assertTrue("--input argument is missging" in msg)

    def test_arguments_no_output_file(self):
        args = [
            "retriever.py",
            "--intput=tmp/input",
            "--mfip",
            "--lfip",
            "--eps",
            "--bytes"
        ]

        valid_args, _, _, _, msg = Retriever.validate_arguments(args)
        self.assertFalse(valid_args)
        self.assertTrue("--output argument is missging" in msg)

    def test_arguments_bad_input_file_flag_separator(self):
        args = [
            "retriever.py",
            "--input:tmp/input",
            "--output=tmp/output/output.json",
            "--mfip",
            "--lfip",
            "--eps",
            "--bytes"
        ]

        valid_args, _, _, _, msg = Retriever.validate_arguments(args)
        self.assertFalse(valid_args)
        self.assertTrue("Use '=' to asign a path to --input value" in msg)

    def test_arguments_bad_input_file(self):
        args = [
            "retriever.py",
            "--input=bad_path",
            "--output=tmp/output/output.json",
            "--mfip",
            "--lfip",
            "--eps",
            "--bytes"
        ]

        valid_args, _, _, _, msg = Retriever.validate_arguments(args)
        self.assertFalse(valid_args)
        self.assertTrue("--input path doesn't exist" in msg)

    def test_arguments_bad_output_file_flag_separator(self):
        args = [
            "retriever.py",
            "--input=tmp/input",
            "--output:tmp/output/output.json",
            "--mfip",
            "--lfip",
            "--eps",
            "--bytes"
        ]

        valid_args, _, _, _, msg = Retriever.validate_arguments(args)
        self.assertFalse(valid_args)
        self.assertTrue("Use '=' to asign a path to --output value" in msg)

    def test_arguments_bad_output_file_is_directory(self):
        args = [
            "retriever.py",
            "--input=tmp/input",
            "--output=tmp/output",
            "--mfip",
            "--lfip",
            "--eps",
            "--bytes"
        ]

        valid_args, _, _, _, msg = Retriever.validate_arguments(args)
        self.assertFalse(valid_args)
        self.assertTrue("--output path is a dir and should be a file" in msg)

    def test_arguments_bad_argument(self):
        args = [
            "retriever.py",
            "--input=tmp/input",
            "--output=tmp/output/output.json",
            "--mfip",
            "--lfip",
            "--eps",
            "--bytes",
            "--some_bad_operation_parameter"
        ]

        valid_args, _, _, _, msg = Retriever.validate_arguments(args)
        self.assertFalse(valid_args)
        self.assertTrue(f"{args[7]} argument is not recognized" in msg)

    def test_operation_most_frequent_ip(self):
        operations = [
            {
                "value":"--mfip",
                "description":"Most frequent IP",
                "is_optional":True
            }
        ]

        result = "Client IP '10.105.21.194' appears 4 times and Destination IP '207.58.145.61' appears 6 times"

        self._retriever.set_operations(ops=operations)
        self._retriever.set_dataframe(df=self.get_dataframe())
        operations = self._retriever.apply_operations()
        
        self.assertEqual(operations[0]["description"], "Most frequent IP")
        self.assertEqual(operations[0]["result"], result)

    def test_operation_least_frequent_ip(self):
        operations = [
            {
                "value": "--lfip",
                "description": "Least frequent IP",
                "is_optional": True
            }
        ]

        result = "Client IP '10.105.21.190' appears 1 times and Destination IP '209.73.177.115' appears 1 times"

        self._retriever.set_operations(ops=operations)
        self._retriever.set_dataframe(df=self.get_dataframe())
        operations = self._retriever.apply_operations()

        self.assertEqual(operations[0]["description"], "Least frequent IP")
        self.assertEqual(operations[0]["result"], result)

    def test_operation_events_per_second(self):
        operations = [
            {
                "value": "--eps",
                "description": "Events per second",
                "is_optional": True
            }
        ]

        result = 1.4285714285714286

        self._retriever.set_operations(ops=operations)
        self._retriever.set_dataframe(df=self.get_dataframe())
        operations = self._retriever.apply_operations()

        self.assertEqual(operations[0]["description"], "Events per second")
        self.assertEqual(operations[0]["result"], result)

    def test_operation_bytes_exchanged(self):
        operations = [
            {
                "value": "--bytes",
                "description": "Total amount of bytes exchanged",
                "is_optional": True
            }
        ]

        bytes = 88754
        size, format = utils.bytes_formatter(bytes)
        result = f"{round(size, 2)}{format} in total ({bytes} bytes)"

        self._retriever.set_operations(ops=operations)
        self._retriever.set_dataframe(df=self.get_dataframe())
        operations = self._retriever.apply_operations()

        self.assertEqual(operations[0]["description"], "Total amount of bytes exchanged")
        self.assertEqual(operations[0]["result"], result)

if __name__ == "__main__":
    unittest.main()
