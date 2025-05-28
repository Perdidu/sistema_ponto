# Análise da Regra da Convenção Coletiva para Horas Extras

## Regra da Convenção Coletiva

Conforme informado pelo usuário, a convenção coletiva de trabalho estabelece que:

> Todas as horas extras, independente de dia e horário, devem ser pagas na proporção de as 2 primeiras como 50% e as demais 100% (vale para as horas de interjornada).

## Interpretação e Aplicação

Esta regra modifica a forma padrão de cálculo de horas extras prevista na CLT, que normalmente considera:
- 50% para horas extras em dias úteis
- 100% para horas extras em domingos e feriados

Com a regra da convenção coletiva, o critério passa a ser a quantidade de horas extras trabalhadas no dia, independentemente do tipo de dia (útil, domingo ou feriado) ou do motivo (trabalho adicional ou interjornada):

1. **As 2 primeiras horas extras do dia**: Remuneradas com adicional de 50%
2. **Horas extras excedentes**: Remuneradas com adicional de 100%
3. **Horas de interjornada**: Somadas às horas extras do dia e seguem a mesma regra (2 primeiras a 50%, demais a 100%)

## Exemplos Práticos

### Exemplo 1: Dia útil com 3 horas extras
- Horas regulares: 8h
- Horas extras: 3h
- **Cálculo**: 2h com adicional de 50% + 1h com adicional de 100%

### Exemplo 2: Domingo com 6 horas trabalhadas
- Horas regulares: 0h (todas são extras em domingo)
- Horas extras: 6h
- **Cálculo**: 2h com adicional de 50% + 4h com adicional de 100%

### Exemplo 3: Dia com 1 hora extra + 5 horas de interjornada
- Horas regulares: 8h
- Horas extras normais: 1h
- Horas de interjornada: 5h
- Total de horas extras: 6h
- **Cálculo**: 2h com adicional de 50% + 4h com adicional de 100%

## Implementação no Sistema

O sistema foi ajustado para:

1. Calcular o total de horas extras do dia, incluindo:
   - Horas extras por trabalho além da jornada normal
   - Horas extras por trabalho em dias de descanso (sábados, domingos e feriados)
   - Horas de interjornada (quando o intervalo entre jornadas é menor que 11 horas)

2. Aplicar a regra da convenção coletiva:
   - Se o total de horas extras do dia for menor ou igual a 2 horas, todas são pagas com adicional de 50%
   - Se o total for maior que 2 horas, as 2 primeiras são pagas com adicional de 50% e as demais com adicional de 100%

## Conformidade Legal

Esta implementação está em conformidade com:

1. **Artigo 7º, inciso XXVI da Constituição Federal**: Reconhece as convenções e acordos coletivos de trabalho.

2. **Artigo 611-A da CLT** (incluído pela Reforma Trabalhista - Lei 13.467/2017): Estabelece que a convenção coletiva e o acordo coletivo de trabalho têm prevalência sobre a lei quando dispuserem sobre jornada de trabalho e intervalo intrajornada.

A regra implementada respeita tanto a convenção coletiva quanto os princípios da legislação trabalhista, garantindo o pagamento correto das horas extras conforme o acordado entre as partes.
