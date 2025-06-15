FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5006

CMD ["sh", "-c", "flask init-db && python app.py"] 