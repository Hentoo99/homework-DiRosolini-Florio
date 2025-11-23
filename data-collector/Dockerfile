# Usa un'immagine Python leggera ufficiale
FROM python:3.10-slim

# Variabili d'ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# --- FIX: AGGIUNGI QUESTA PARTE ---
# Installiamo gcc e le librerie di sviluppo MySQL necessarie per compilare
# i driver del database (es. mysqlclient o mysql-connector)
RUN apt-get update \
    && apt-get install -y gcc pkg-config default-libmysqlclient-dev \
    && apt-get clean
# ----------------------------------

# Copia requisiti e installa
COPY data-collector/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice sorgente
COPY data-collector/ .
# Copia la cartella condivisa dei file .proto
COPY proto/ ./proto/

# Comando di avvio
CMD ["python", "main.py"]