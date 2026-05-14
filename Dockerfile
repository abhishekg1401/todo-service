FROM python:3.10-alpine

WORKDIR /todo-service

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data

EXPOSE 8080

CMD ["python3", "run.py"]