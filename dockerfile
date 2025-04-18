FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y wget unzip curl openssh-client iputils-ping && \
    rm -rf /var/lib/apt/lists/*

ENV TERRAFORM_VERSION=1.10.2

RUN wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    mv terraform /usr/local/bin/ && \
    rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip

RUN mkdir /iaac
VOLUME /iaac


RUN mkdir Downloads &&\
          cd Downloads && \
          curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" &&\
        unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf /Downloads

# Criar diretório para a aplicação
WORKDIR /app

# Copiar o arquivo requirements.txt para o contêiner
COPY requirements.txt /app/

# Instalar pacotes do Python usando o requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /iaac

# Definir o comando padrão para execução quando o container for iniciado
CMD ["/bin/bash"]