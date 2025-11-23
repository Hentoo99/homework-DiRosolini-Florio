# 1. Immagine di base
FROM python:3.10-slim

# 2. Ottimizzazioni Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Cartella di lavoro
WORKDIR /app

# 4. Installazione dipendenze di sistema per MySQL
# pkg-config e default-libmysqlclient-dev servono per compilare mysqlclient
RUN apt-get update \
    && apt-get install -y gcc pkg-config default-libmysqlclient-dev \
    && apt-get clean

# 5. Installazione dipendenze Python
COPY user-manager/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copia del codice
COPY user-manager/ .
COPY proto/ ./proto/

# 7. Avvio
CMD ["python", "main.py"]