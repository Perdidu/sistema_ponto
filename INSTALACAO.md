# Guia de Instalação do Sistema de Controle de Ponto

Este guia fornece instruções detalhadas para instalar, configurar e executar o Sistema de Controle de Ponto em diferentes ambientes.

## Requisitos do Sistema

- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)
- Banco de dados: SQLite (incluído) ou MySQL (opcional)
- Navegador web moderno (Chrome, Firefox, Edge, Safari)
- Mínimo de 2GB de RAM e 1GB de espaço em disco

## Instalação Passo a Passo

### 1. Preparação do Ambiente

1. Descompacte o arquivo `sistema_ponto.zip` em um diretório de sua escolha
2. Abra um terminal ou prompt de comando
3. Navegue até a pasta do projeto:
   ```
   cd caminho/para/sistema_ponto
   ```

### 2. Criação do Ambiente Virtual

O ambiente virtual isola as dependências do projeto, evitando conflitos com outros pacotes Python instalados no sistema.

**Windows:**
```
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```
python3 -m venv venv
source venv/bin/activate
```

Você saberá que o ambiente virtual está ativo quando o nome `(venv)` aparecer no início da linha de comando.

### 3. Instalação das Dependências

Com o ambiente virtual ativado, instale todas as dependências necessárias:

```
pip install -r requirements.txt
```

Este comando instalará automaticamente todos os pacotes Python necessários para o funcionamento do sistema.

## Configuração do Banco de Dados

### Opção 1: SQLite (Padrão, mais simples)

Por padrão, o sistema está configurado para usar SQLite, que não requer instalação adicional. O banco de dados será criado automaticamente na primeira execução.

### Opção 2: MySQL (Recomendado para produção)

Para usar MySQL:

1. Instale o MySQL Server em seu sistema, se ainda não estiver instalado
2. Crie um banco de dados para o sistema:
   ```sql
   CREATE DATABASE sistema_ponto CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Crie um usuário com permissões para este banco:
   ```sql
   CREATE USER 'usuario_ponto'@'localhost' IDENTIFIED BY 'sua_senha';
   GRANT ALL PRIVILEGES ON sistema_ponto.* TO 'usuario_ponto'@'localhost';
   FLUSH PRIVILEGES;
   ```
4. Edite o arquivo `src/main.py` e localize a seção de configuração do banco de dados:
   ```python
   # Configuração SQLite (padrão)
   app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema_ponto.db'
   
   # Configuração MySQL (descomentada)
   # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://usuario_ponto:sua_senha@localhost/sistema_ponto'
   ```
5. Comente a linha do SQLite e descomente a linha do MySQL, substituindo `usuario_ponto`, `sua_senha` e `localhost` pelos valores corretos para seu ambiente.

## Inicialização do Sistema

### Primeira Execução

Na primeira execução, o sistema criará automaticamente as tabelas no banco de dados:

```
python -m src.main
```

### Execução Normal

Para iniciar o sistema:

1. Ative o ambiente virtual (se ainda não estiver ativo)
2. Execute o comando:
   ```
   python -m src.main
   ```
3. Acesse o sistema no navegador: `http://localhost:5000`

### Configuração de Porta

Por padrão, o sistema usa a porta 5000. Para alterar, edite o arquivo `src/main.py` e modifique a linha:

```python
app.run(host='0.0.0.0', port=5000)
```

## Implantação em Produção

Para ambientes de produção, recomendamos:

1. Usar MySQL como banco de dados
2. Configurar um servidor WSGI como Gunicorn ou uWSGI
3. Usar um proxy reverso como Nginx ou Apache

### Exemplo com Gunicorn e Nginx

1. Instale o Gunicorn:
   ```
   pip install gunicorn
   ```

2. Crie um arquivo `wsgi.py` na raiz do projeto:
   ```python
   from src.main import app
   
   if __name__ == "__main__":
       app.run()
   ```

3. Execute o Gunicorn:
   ```
   gunicorn --bind 0.0.0.0:8000 wsgi:app
   ```

4. Configure o Nginx como proxy reverso (exemplo de configuração):
   ```
   server {
       listen 80;
       server_name seu_dominio.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## Backup e Restauração

### Backup do SQLite

```
cp sistema_ponto.db sistema_ponto_backup_$(date +%Y%m%d).db
```

### Backup do MySQL

```
mysqldump -u usuario_ponto -p sistema_ponto > sistema_ponto_backup_$(date +%Y%m%d).sql
```

### Restauração do SQLite

```
cp sistema_ponto_backup_YYYYMMDD.db sistema_ponto.db
```

### Restauração do MySQL

```
mysql -u usuario_ponto -p sistema_ponto < sistema_ponto_backup_YYYYMMDD.sql
```

## Solução de Problemas

### Erro de Conexão com o Banco de Dados

- Verifique se as credenciais do banco estão corretas
- Confirme se o serviço do MySQL está em execução
- Verifique se o banco de dados foi criado

### Erro ao Iniciar o Sistema

- Confirme que todas as dependências foram instaladas
- Verifique se o ambiente virtual está ativado
- Confira os logs de erro para identificar o problema específico

### Problemas de Permissão

- Verifique se o usuário tem permissão para escrever no diretório do projeto
- No Linux/Mac, pode ser necessário ajustar permissões: `chmod -R 755 sistema_ponto`

## Suporte

Para obter suporte adicional, consulte a documentação completa na pasta `docs/` ou entre em contato com a equipe de desenvolvimento.
