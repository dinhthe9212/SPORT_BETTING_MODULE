FROM python:3.11-slim-buster

WORKDIR /app

COPY sports_data_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared module first
COPY shared /app/shared

COPY sports_data_service/ .

EXPOSE 8005

CMD ["python", "manage.py", "runserver", "0.0.0.0:8005"]


