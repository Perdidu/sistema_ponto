# Manual do Usuário - Sistema de Controle de Ponto

Este manual fornece instruções detalhadas sobre como utilizar o Sistema de Controle de Ponto, incluindo todas as funcionalidades disponíveis e fluxos de trabalho recomendados.

## Índice

1. [Visão Geral](#visão-geral)
2. [Primeiros Passos](#primeiros-passos)
3. [Cadastro de Funcionários](#cadastro-de-funcionários)
4. [Registro de Ponto](#registro-de-ponto)
5. [Cadastro de Feriados](#cadastro-de-feriados)
6. [Cálculos e Relatórios](#cálculos-e-relatórios)
7. [Entrada Manual de Registros](#entrada-manual-de-registros)
8. [Importação de Planilhas](#importação-de-planilhas)
9. [Cálculo Detalhado](#cálculo-detalhado)
10. [Dicas e Boas Práticas](#dicas-e-boas-práticas)

## Visão Geral

O Sistema de Controle de Ponto foi desenvolvido para gerenciar o registro de ponto de funcionários conforme as leis trabalhistas brasileiras. Ele permite:

- Cadastrar funcionários e seus dados salariais
- Registrar entradas e saídas, incluindo horários de almoço
- Cadastrar feriados para cálculos corretos
- Calcular automaticamente horas extras, adicional noturno e DSR
- Gerar relatórios financeiros baseados no salário

## Primeiros Passos

Ao acessar o sistema pela primeira vez, você verá a tela inicial com o menu lateral à esquerda. Este menu contém todas as funcionalidades disponíveis:

- **Início**: Página inicial do sistema
- **Funcionários**: Cadastro e gerenciamento de funcionários
- **Registros de Ponto**: Registro e visualização de pontos
- **Feriados**: Cadastro e gerenciamento de feriados
- **Cálculos**: Relatórios financeiros gerais
- **Cálculo Detalhado**: Relatórios detalhados por dia
- **Entrada Manual**: Registro manual de horas extras
- **Importar Planilha**: Importação de registros via planilha

## Cadastro de Funcionários

### Adicionar Novo Funcionário

1. Clique em "Funcionários" no menu lateral
2. Clique no botão "Novo Funcionário"
3. Preencha os campos obrigatórios:
   - Nome completo
   - Cargo
   - Salário mensal
   - Data de admissão
4. Clique em "Salvar"

### Editar Funcionário

1. Clique em "Funcionários" no menu lateral
2. Localize o funcionário na lista
3. Clique no ícone de edição (lápis)
4. Atualize os campos necessários
5. Clique em "Salvar"

### Excluir Funcionário

1. Clique em "Funcionários" no menu lateral
2. Localize o funcionário na lista
3. Clique no ícone de exclusão (lixeira)
4. Confirme a exclusão

## Registro de Ponto

### Novo Registro de Ponto

1. Clique em "Registros de Ponto" no menu lateral
2. Clique no botão "Novo Registro"
3. Selecione o funcionário
4. Selecione a data
5. Preencha os horários do período regular:
   - Horário de Entrada
   - Horário de Saída para Almoço (opcional)
   - Horário de Retorno do Almoço (opcional)
   - Horário de Saída
6. Se necessário, adicione períodos adicionais clicando em "Adicionar Período Adicional"
7. Adicione observações se necessário
8. Clique em "Salvar"

### Visualizar Registros

1. Clique em "Registros de Ponto" no menu lateral
2. Use os filtros para localizar registros específicos:
   - Funcionário
   - Período (data inicial e final)
3. Clique em "Filtrar"

### Editar Registro

1. Clique em "Registros de Ponto" no menu lateral
2. Localize o registro na lista
3. Clique no ícone de edição (lápis)
4. Atualize os campos necessários
5. Clique em "Salvar"

## Cadastro de Feriados

### Adicionar Novo Feriado

1. Clique em "Feriados" no menu lateral
2. Clique no botão "Novo Feriado"
3. Preencha os campos:
   - Nome do feriado
   - Data
   - Descrição (opcional)
4. Clique em "Salvar"

### Editar ou Excluir Feriado

1. Clique em "Feriados" no menu lateral
2. Localize o feriado na lista
3. Clique no ícone de edição (lápis) ou exclusão (lixeira)
4. Faça as alterações necessárias ou confirme a exclusão

## Cálculos e Relatórios

### Gerar Relatório de Cálculos

1. Clique em "Cálculos" no menu lateral
2. Selecione os filtros:
   - Funcionário (ou "Todos")
   - Período (mês/ano)
3. Clique em "Calcular"
4. O sistema exibirá um resumo com:
   - Horas regulares
   - Horas extras 50%
   - Horas extras 100%
   - Adicional noturno
   - DSR sobre horas extras
   - Valores financeiros correspondentes

## Entrada Manual de Registros

Esta funcionalidade permite inserir registros de horas extras diretamente na interface, sem necessidade de importação de planilhas.

### Adicionar Registros Manualmente

1. Clique em "Entrada Manual" no menu lateral
2. Na tabela editável, preencha:
   - Nome do Funcionário (exatamente como cadastrado)
   - Data (formato DD/MM/YY)
   - Hora Extra Inicial (formato HH:MM)
   - Hora Extra Final (formato HH:MM)
3. Para adicionar mais registros, clique em "Adicionar Linha"
4. Para remover um registro, clique no ícone de lixeira
5. Quando terminar, clique em "Salvar Todos os Registros"

### Dicas para Entrada Manual

- O nome do funcionário deve corresponder exatamente ao cadastrado no sistema
- Para períodos que cruzam a meia-noite, o sistema detectará automaticamente
- Você pode adicionar quantas linhas forem necessárias antes de salvar

## Importação de Planilhas

Esta funcionalidade permite importar múltiplos registros de ponto a partir de uma planilha Excel.

### Importar Registros via Planilha

1. Clique em "Importar Planilha" no menu lateral
2. Baixe o modelo de planilha clicando em "Baixar Modelo"
3. Preencha a planilha seguindo o formato do modelo
4. Salve a planilha preenchida
5. Clique em "Escolher Arquivo" e selecione a planilha
6. Clique em "Importar"

### Formato da Planilha

A planilha deve conter as seguintes colunas:
- Nome do Funcionário
- Data (DD/MM/YYYY)
- Hora de Entrada
- Hora de Saída para Almoço (opcional)
- Hora de Retorno do Almoço (opcional)
- Hora de Saída

## Cálculo Detalhado

Esta funcionalidade permite visualizar os cálculos detalhados por dia, incluindo a classificação das horas extras.

### Gerar Relatório Detalhado

1. Clique em "Cálculo Detalhado" no menu lateral
2. Selecione os filtros:
   - Funcionário (ou "Todos")
   - Data Inicial
   - Data Final
3. Clique em "Filtrar"
4. O sistema exibirá uma tabela com detalhamento diário:
   - Data
   - Dia da Semana
   - Funcionário
   - Horas Regulares
   - Horas Extras 50%
   - Horas Extras 100%
   - Horas Noturnas
   - Interjornada

### Resumo Financeiro

Abaixo da tabela detalhada, o sistema exibe um resumo financeiro com:
- Horas Extras 50% (quantidade e valor)
- Horas Extras 100% (quantidade e valor)
- Adicional Noturno (quantidade e valor)
- Interjornada (quantidade e valor)
- DSR sobre Horas Extras (valor)
- Total (valor)

## Dicas e Boas Práticas

### Registro de Ponto

- Registre os pontos diariamente para evitar acúmulo
- Verifique se os horários estão corretos antes de salvar
- Adicione observações para justificar situações atípicas

### Cálculos

- Verifique se todos os feriados estão cadastrados corretamente
- Confira se o salário dos funcionários está atualizado
- Gere relatórios mensais para acompanhamento

### Segurança

- Não compartilhe suas credenciais de acesso
- Faça backup regular dos dados
- Encerre sua sessão ao sair do sistema

### Conformidade Legal

- O sistema segue as regras da CLT para cálculo de horas extras
- Respeita o intervalo interjornada de 11 horas
- Aplica as regras de convenção coletiva para classificação de horas extras (50% e 100%)
- Calcula corretamente o adicional noturno (20%)
- Considera o DSR sobre horas extras conforme legislação

Para mais informações sobre a conformidade legal do sistema, consulte os documentos na pasta `docs/`.
