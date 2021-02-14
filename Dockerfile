FROM python:3.9-alpine

COPY entrypoint.py /entrypoint.py
RUN pip install markdown pygithub requests
ENTRYPOINT ["python", "/entrypoint.py"]
