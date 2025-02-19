# Imagem base do Python
FROM python:3.13.2-alpine3.21

# Define o diretório de trabalho
WORKDIR /app

# Instala as dependências do sistema
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev

# Copia os arquivos de requisitos
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte
COPY . .

# Cria diretórios necessários
RUN mkdir -p data

# Comando para executar o bot
CMD ["python", "main.py"]
