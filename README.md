# LOG RETRIEVER
A python & Flask script made by Saul Maldonado
## About Log retriever
This is a python script that will produce statistics (in json txt format) related to http access.
Although this project includes some csv files for processing (located in tmp/input folder), you can download and decompress the full log access file from https://www.secrepo.com/squid/access.log.gz
## Running in your local machine
### How to build the environment
1. You must need python +3.8 installed in your machine
2. Create and activate a virtual environment
```bash
python3 -m venv /path/to/new/virtual/environment
venv\\Scripts\\activate.bat (windows)
source venv/bin/activate (linux)
```
3. Install required packages
```bash
pip install -r requirements.txt
```
### How to run the script
1. Local run: follow the menu after executing below's script
```bash
python retriever.py
```
2. Local unittesting
```bash
python retriever_test.py
```
## Running in Docker
### Create Docker image
1. You must need Docker installed in your machine
2. Build Docker image
```bash
 docker build -t retriever-image:latest .
```
### Run Docker image
1. Go to Docker and manually run image retriever-image:latest
2. Click the created cntainer and open the terminal.
3. Docker run: follow the menu after executing below's script
```bash
cd app
python retriever.py
```
4. Local unittesting
```bash
cd app
python retriever_test.py
```