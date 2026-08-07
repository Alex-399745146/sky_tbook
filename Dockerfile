# указывает базовый образ, от которого будет построен новый образ.
FROM python:3.13-slim

# устанавливает переменные окружения.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.4 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

ENV PATH="$POETRY_HOME/bin:$PATH"

# устанавливает рабочую директорию для выполнения последующих инструкций.
WORKDIR /app

# копирует файлы и каталоги с вашего компьютера в контейнер.
COPY pyproject.toml poetry.lock /app/

# выполняет команды в контейнере, такие как установка зависимостей.
RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}" \
    && poetry install --no-interaction --no-ansi

COPY . /app/

# объявление порта, не доступен снаружи.
EXPOSE 8000

# определяет команду, которая будет выполнена при запуске контейнера.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
