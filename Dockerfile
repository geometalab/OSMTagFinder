FROM python:2.7

WORKDIR /app

COPY OSMTagFinder/requirements.txt .
RUN pip install -r requirements.txt

COPY OSMTagFinder/ .

EXPOSE 5000
CMD ["python", "server.py"]
