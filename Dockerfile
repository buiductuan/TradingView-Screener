# Sử dụng base image Python nhẹ
FROM python:3.12-slim

# Cài đặt Poetry
RUN python -m pip install --upgrade pip && pip install poetry

# Đặt thư mục làm việc
WORKDIR /app/src

# Sao chép các tệp cấu hình Poetry
COPY pyproject.toml poetry.lock ./

# Cài đặt các phụ thuộc (không tạo virtual environment)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Sao chép mã nguồn ứng dụng
COPY . .

# Expose cổng cho ứng dụng
EXPOSE 8000

# Lệnh chạy ứng dụng
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
