FROM python:3.10

WORKDIR /app

# Сначала скопируем файл requirements.txt
COPY requirements.txt .

# Установим зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Теперь скопируем остальной проект
COPY . .

# Запускаем приложение
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
