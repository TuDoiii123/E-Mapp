FROM python:3.11-slim

# Cài system deps cần cho psycopg2 và build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements trước để tận dụng Docker layer cache
COPY requirements.txt .

# Cài PyTorch CPU-only trước (nhỏ hơn ~3GB so với CUDA version)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Cài các package còn lại
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source
COPY . .

# Tạo thư mục cần thiết
RUN mkdir -p uploads data/pdf_cache

EXPOSE 8888

CMD ["python", "server.py"]
