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
```

## Infraestrutura Provisionada (IaC com Terraform)

---

### ☁️ Amazon S3

- Bucket S3 criado: `s3-273354626311`.
- **Finalidade**: armazenar arquivos da aplicação, como:
  - Scripts;
  - Modelos de machine learning;
  - Dados;
  - Código da API.
- Inclui provisionamento com `local-exec` para:
  - Upload inicial dos arquivos;
  - Remoção automática no `terraform destroy`.

---

### 🖥️ Instância EC2

- Tipo: `t2.micro` com Amazon Linux.
- **Função**: executar uma API feita com FastAPI.

Durante o `user_data`, a instância:
- Atualiza pacotes (`yum update`);
- Instala dependências com `pip`;
- Instala a AWS CLI;
- Sincroniza arquivos do S3 para `/ml_app`;
- Inicia a aplicação com:
  ```bash
  nohup python3 api.py &
  ```

---

### 🔒 Security Group

- Nome: `ml_api`
- Regras de entrada (Ingress):
  - Porta **8080** liberada (acesso à API);
  - Porta **22** liberada (acesso via SSH).
- Regras de saída (Egress):
  - Todas as portas (0–65535) liberadas.

> ⚠️ Este Security Group está associado à instância EC2 e à **VPC padrão** da AWS.

---

### 👤 Permissões IAM (Acesso EC2 ↔ S3)

Para permitir que a EC2 acesse o S3, foram criados:

1. **IAM Role**: `ec2_s3_role_access`
   - EC2 pode assumir essa role (`ec2.amazonaws.com`).

2. **IAM Policy**: `s3_access_policy`
   - Permissões: `s3:GetObject`, `s3:PutObject`, `s3:ListBucket`.

3. **IAM Instance Profile**: `ec2_s3_profile`
   - Conecta a role à instância EC2.

---

### 📌 Diagrama Resumido

```text
S3 <---- (acesso via IAM) ---- EC2
             |
             +-- Instance Profile
                 |
                 +-- IAM Role
                     |
                     +-- IAM Policy (S3 Access)

EC2 <---> Security Group
         |-- Ingress: 8080 (HTTP), 22 (SSH)
         |-- Egress: Full (0–65535)
```
