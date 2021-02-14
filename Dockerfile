FROM python:3.9-alpine

COPY entrypoint.py /entrypoint.py
RUN pip install markdown pygithub
RUN pip install -U requests[socks]
ENTRYPOINT ["python", "/entrypoint.py"]
