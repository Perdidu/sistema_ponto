# Instruções para Instalação e Uso do Sistema de Ponto

Este documento contém instruções para instalar e utilizar o Sistema de Ponto com a nova funcionalidade de tabela editável para entrada manual de registros.

## Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)
- MySQL (opcional, pode usar SQLite para testes)

## Instalação

1. Descompacte o arquivo `sistema_ponto_tabela_editavel.zip`
2. Navegue até a pasta do projeto:
   ```
   cd sistema_ponto
   ```
3. Crie um ambiente virtual:
   ```
   python -m venv venv
   ```
4. Ative o ambiente virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
5. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

## Configuração do Banco de Dados

Por padrão, o sistema usa SQLite para facilitar os testes. Se preferir usar MySQL:

1. Edite o arquivo `src/main.py`
2. Descomente a linha de configuração do MySQL
3. Configure as variáveis de ambiente para conexão com o banco:
   - `DB_USERNAME`: nome de usuário do MySQL
   - `DB_PASSWORD`: senha do MySQL
   - `DB_HOST`: host do MySQL (geralmente localhost)
   - `DB_PORT`: porta do MySQL (geralmente 3306)
   - `DB_NAME`: nome do banco de dados

## Executando o Sistema

1. Com o ambiente virtual ativado, execute:
   ```
   python -m src.main
   ```
2. Acesse o sistema no navegador: `http://localhost:5000`

## Nova Funcionalidade: Tabela Editável para Entrada Manual

A nova funcionalidade permite inserir registros de horas extras através de uma tabela editável diretamente na interface web:

1. Acesse a opção "Entrada Manual" no menu lateral
2. Use a tabela para adicionar, editar ou remover registros:
   - Clique em "Adicionar Linha" para inserir novos registros
   - Preencha os campos: Nome do Funcionário, Data, Hora Extra Inicial e Hora Extra Final
   - Use o ícone de lixeira para remover linhas indesejadas
3. Clique em "Salvar Todos os Registros" para processar os dados
4. O sistema validará os registros e exibirá um relatório dos resultados

## Dicas de Uso

- O nome do funcionário deve corresponder exatamente ao cadastrado no sistema
- Use o formato DD/MM/YY para datas (exemplo: 01/03/25)
- Use o formato HH:MM para horários (exemplo: 03:00)
- Para períodos que cruzam a meia-noite, o sistema detectará automaticamente
- Você pode adicionar quantas linhas forem necessárias antes de salvar

## Suporte

Se encontrar problemas ou tiver dúvidas, entre em contato com o suporte técnico.
