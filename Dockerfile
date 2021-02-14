FROM python:3.9-alpine

COPY entrypoint.py /entrypoint.py

ENTRYPOINT ["python", "/entrypoint.py"]