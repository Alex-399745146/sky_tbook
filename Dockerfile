FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DOCKER_CONTAINER=1

WORKDIR /app

COPY requirements-docker.txt /app/
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY . /app/

EXPOSE 8000

# По умолчанию запускаем Django, но можно переопределить в docker-compose.yml
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]