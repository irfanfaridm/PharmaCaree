# Menggunakan citra dasar Python
FROM python:3.11-slim

# Mengatur direktori kerja di dalam kontainer
WORKDIR /app

# Menyalin file requirements.txt dan menginstal dependensi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin semua kode aplikasi ke dalam kontainer
COPY . .

# Mengekspos port yang digunakan oleh Flask
EXPOSE 5005

# Menentukan perintah untuk menjalankan aplikasi Flask
CMD ["python", "main.py"] 