FROM python:3.10-slim

WORKDIR /app

ADD requirements.txt /app/
RUN pip install pip -U \
    && pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

CMD ["python", "-m", "run"]