FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY d-id_upload_service.py ./

# Optional: copy .env if you want to bake it in (not recommended for secrets)
# COPY .env ./

EXPOSE 5100

CMD ["python", "d-id_upload_service.py"] 