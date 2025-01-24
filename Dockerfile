FROM python:3.12.8-slim

WORKDIR /app

COPY ./code/requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./code/. .

EXPOSE 8080

CMD ["python3", "main.py"]