FROM python:3.9.6

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade -r requirements.txt

COPY src .

COPY .env .

CMD ["python", "main.py"]