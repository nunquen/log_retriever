FROM python:3.8

# INstalling environment
ENV VIRTUAL_ENV=/opt/venv
RUN python -m pip install --upgrade pip
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt

# Creating app folder
RUN mkdir -p /app
COPY configuration /app/configuration
COPY libs app/libs
COPY logs app/logs
COPY tmp app/tmp
COPY retriever.py app/.
COPY retriever_test.py app/.

# Run the application:
#CMD ["python", "app/retriever.py"]
