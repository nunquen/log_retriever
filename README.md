# LOG RETRIEVER
A python & Flask script made by Saul Maldonado
## How to build the environment
1. You must need python +3.8 installed in your machine
2. Create and activate a virtual environment
```bash
python3 -m venv /path/to/new/virtual/environment
venv\\Scripts\\activate.bat (windows)
```
3. Install required packages
```bash
pip install -r requirements.txt
```
4. Download test csv data from https://www.secrepo.com/squid/access.log.gz and decompress the zip file.
   (you can use this file as input file to run the script)

## How to run the script
1. Local run: follow the menu
```bash
python retriever.py
```
2. Local unittesting
```bash
python retriever_test.py
```