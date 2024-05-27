FROM python:3.9.6

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 1883

CMD ["python", "main.py"]
