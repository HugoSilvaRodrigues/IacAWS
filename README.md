
# Configuração Docker para IaC com Terraform

## Execução com Docker + Terraform

### Passos completos

```bash
# 1. Criar a imagem Docker
docker build -t imagem_iac .

# 2. Iniciar o container (substitua o caminho pelo da sua máquina)
docker run -dit -v "/caminho/absoluto/para/pasta":/iac --name container_iac imagem_iac

# 3. Acessar o container
docker exec -it container_iac bash

# 4. Dentro do container, navegar para a pasta e executar os comandos Terraform
cd /iac
terraform init
aws configure
terraform plan
terraform apply -auto-approve

## Infraestrutura Provisionada (IaC com Terraform)

---

### Amazon S3

- Criado um bucket S3 chamado `s3-273354626311`.
- **Finalidade**: Armazenar arquivos da aplicação, como:
  - Scripts,
  - Modelos de machine learning,
  - Dados,
  - Código da API.
- Inclui provisionamento `local-exec` para:
  - Fazer o upload inicial dos arquivos.
  - Remover os arquivos automaticamente do bucket ao destruir o recurso (`terraform destroy`).

---

### Instância EC2

- Criada uma instância EC2 `t2.micro` com Amazon Linux.
- **Função**: Executar uma API FastAPI continuamente.

Durante o `user_data`, a instância:
- Atualiza pacotes (`yum update`).
- Instala dependências com `pip`.
- Instala a AWS CLI.
- Sincroniza arquivos do S3 para `/ml_app`.
- Inicia a aplicação com `nohup python3 api.py &`.

---

### Security Group

- Criado um **Security Group** chamado `ml_api` com as seguintes regras:

**Ingress (entrada):**
- Porta **8080** liberada para acesso externo (API).
- Porta **22** liberada para acesso SSH.

**Egress (saída):**
- Liberação total (portas 0 a 65535) para comunicação externa da EC2.

> ⚠️ Este Security Group está associado à instância EC2 e à **VPC padrão** da AWS .

---

### 👤 Permissões IAM (Acesso EC2 ↔ S3)

Para a instância EC2 acessar o bucket S3, foram criados:

1. **IAM Role** (`ec2_s3_role_access`)
   - Permite que instâncias EC2 assumam essa role (`ec2.amazonaws.com`).

2. **IAM Policy** (`s3_access_policy`)
   - Concede permissões: `s3:GetObject`, `s3:PutObject`, `s3:ListBucket`.
   - Anexada à Role.

3. **IAM Instance Profile** (`ec2_s3_profile`)
   - Conecta a Role à EC2.
   - Referenciado diretamente na definição do recurso `aws_instance`.

---


### Diagrama Resumido


S3 <---- (accessed by) ---- EC2 | +-- Permissions: EC2 --> Instance Profile --> IAM Role --> IAM Policy (S3 Access)

EC2 <---> Security Group (Permissões de rede) | +-- Ingress: 8080 (HTTP), 22 (SSH) +-- Egress: Full (0-65535)
