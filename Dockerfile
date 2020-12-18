FROM python:3.6-slim
ADD . /data
WORKDIR /data
RUN pip install --no-cache-dir -r requirement.txt .
