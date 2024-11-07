# Use uma imagem base oficial do Python
FROM python:3.12-slim

# Defina o diretório de trabalho dentro do container
WORKDIR /app

# Copie os arquivos de requisitos (se houver) e instale as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie o código-fonte para o container
COPY . .

EXPOSE 8080

# Defina o comando para rodar o serviço quando o container iniciar
CMD ["python3", "main.py"]
