FROM python:3.9-alpine
COPY server.py server.py
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 2000
ENTRYPOINT ["python3", "server.py"]