from datetime import datetime, date, timedelta
from decimal import Decimal

# Função para calcular a diferença em horas entre dois horários
def calculate_hours_difference(start_time, end_time):
    if not start_time or not end_time:
        return Decimal('0.0')
    
    # Converter para datetime para facilitar o cálculo
    start_dt = datetime.combine(date.today(), start_time)
    end_dt = datetime.combine(date.today(), end_time)
    
    # Se o horário final for menor que o inicial, adiciona um dia
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
    
    # Calcula a diferença em horas (decimal)
    diff_seconds = (end_dt - start_dt).total_seconds()
    diff_hours = Decimal(str(diff_seconds / 3600))
    
    # Arredonda para 2 casas decimais
    return diff_hours.quantize(Decimal('0.01'))

# Função para verificar se o horário está no período noturno
def is_night_time(time_obj):
    night_start = datetime.strptime('22:00', '%H:%M').time()
    night_end = datetime.strptime('05:00', '%H:%M').time()
    
    if night_start <= time_obj or time_obj <= night_end:
        return True
    return False

# Função para calcular as horas noturnas entre dois horários
def calculate_night_hours(start_time, end_time):
    if not start_time or not end_time:
        return Decimal('0.0')
    
    night_start = datetime.strptime('22:00', '%H:%M').time()
    night_end = datetime.strptime('05:00', '%H:%M').time()
    
    # Converter para datetime para facilitar o cálculo
    start_dt = datetime.combine(date.today(), start_time)
    end_dt = datetime.combine(date.today(), end_time)
    
    # Se o horário final for menor que o inicial, adiciona um dia
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
    
    # Calcular período noturno
    night_start_dt = datetime.combine(date.today(), night_start)
    night_end_dt = datetime.combine(date.today(), night_end)
    
    # Se o fim do período noturno for no dia seguinte
    if night_end < night_start:
        night_end_dt += timedelta(days=1)
    
    # Verificar sobreposição
    night_hours = Decimal('0.0')
    
    # Caso 1: Início e fim dentro do período noturno
    if (night_start <= start_time or start_time <= night_end) and (night_start <= end_time or end_time <= night_end):
        night_hours = calculate_hours_difference(start_time, end_time)
    
    # Caso 2: Apenas o início está no período noturno
    elif night_start <= start_time or start_time <= night_end:
        if start_time <= night_end:
            # Início entre 00:00 e 05:00
            night_end_dt = datetime.combine(date.today(), night_end)
            overlap_seconds = (night_end_dt - start_dt).total_seconds()
        else:
            # Início entre 22:00 e 23:59
            night_end_dt = datetime.combine(date.today() + timedelta(days=1), night_end)
            overlap_seconds = (night_end_dt - start_dt).total_seconds()
        
        night_hours = Decimal(str(overlap_seconds / 3600)).quantize(Decimal('0.01'))
    
    # Caso 3: Apenas o fim está no período noturno
    elif night_start <= end_time or end_time <= night_end:
        if end_time <= night_end:
            # Fim entre 00:00 e 05:00
            night_start_dt = datetime.combine(date.today() - timedelta(days=1), night_start)
            overlap_seconds = (end_dt - night_start_dt).total_seconds()
        else:
            # Fim entre 22:00 e 23:59
            night_start_dt = datetime.combine(date.today(), night_start)
            overlap_seconds = (end_dt - night_start_dt).total_seconds()
        
        night_hours = Decimal(str(overlap_seconds / 3600)).quantize(Decimal('0.01'))
    
    # Caso 4: Período abrange todo o horário noturno
    elif start_dt < night_start_dt and end_dt > night_end_dt:
        overlap_seconds = (night_end_dt - night_start_dt).total_seconds()
        night_hours = Decimal(str(overlap_seconds / 3600)).quantize(Decimal('0.01'))
    
    return night_hours

# Classe mock para simular períodos de trabalho
class MockPeriod:
    def __init__(self, period_type, entry_time=None, lunch_start=None, lunch_end=None, exit_time=None):
        self.period_type = period_type
        self.entry_time = entry_time
        self.lunch_start = lunch_start
        self.lunch_end = lunch_end
        self.exit_time = exit_time

# Função para converter string para time
def str_to_time(time_str):
    if not time_str:
        return None
    return datetime.strptime(time_str, '%H:%M').time()

# Função para calcular horas trabalhadas em um dia
def test_calculate_day_hours(periods, is_weekend_or_holiday=False):
    """
    Calcula as horas trabalhadas em um dia
    
    Args:
        periods: Lista de períodos de trabalho do dia
        is_weekend_or_holiday: Se é fim de semana ou feriado
        
    Returns:
        Tupla com (horas_regulares, horas_extras_total, horas_noturnas)
    """
    # Inicializar contadores
    regular_hours = Decimal('0.0')
    overtime_hours = Decimal('0.0')
    night_hours = Decimal('0.0')
    
    # Horas regulares máximas por dia
    workday_hours = Decimal('8.0')  # 8 horas por dia
    
    # Processar cada período
    for period in periods:
        # Período regular com almoço
        if period.period_type == 'regular':
            # Período da manhã
            morning_hours = Decimal('0.0')
            if period.entry_time and period.lunch_start:
                morning_hours = calculate_hours_difference(period.entry_time, period.lunch_start)
                night_hours += calculate_night_hours(period.entry_time, period.lunch_start)
            
            # Período da tarde
            afternoon_hours = Decimal('0.0')
            if period.lunch_end and period.exit_time:
                afternoon_hours = calculate_hours_difference(period.lunch_end, period.exit_time)
                night_hours += calculate_night_hours(period.lunch_end, period.exit_time)
            
            # Total de horas no período regular
            period_hours = morning_hours + afternoon_hours
        
        # Período extra (sem almoço)
        else:
            period_hours = Decimal('0.0')
            if period.entry_time and period.exit_time:
                period_hours = calculate_hours_difference(period.entry_time, period.exit_time)
                night_hours += calculate_night_hours(period.entry_time, period.exit_time)
        
        # Distribuir as horas entre regulares e extras
        if not is_weekend_or_holiday:
            # Se ainda não completou a jornada regular
            if regular_hours < workday_hours:
                # Quanto ainda falta para completar a jornada regular
                remaining_regular = workday_hours - regular_hours
                
                # Se o período atual é menor ou igual ao que falta
                if period_hours <= remaining_regular:
                    regular_hours += period_hours
                else:
                    regular_hours += remaining_regular
                    overtime_hours += (period_hours - remaining_regular)
            else:
                # Já completou a jornada regular, tudo é hora extra
                overtime_hours += period_hours
        else:
            # Fim de semana ou feriado: todas as horas são extras
            overtime_hours += period_hours
    
    return (regular_hours, overtime_hours, night_hours)

# Função para aplicar a regra da convenção coletiva às horas extras
def apply_overtime_convention_rule(total_overtime_hours):
    """
    Aplica a regra da convenção coletiva: 2 primeiras horas extras a 50%, demais a 100%
    
    Args:
        total_overtime_hours: Total de horas extras do dia
        
    Returns:
        Tupla com (horas_extras_50, horas_extras_100)
    """
    if total_overtime_hours <= Decimal('2.0'):
        # Todas as horas extras são 50%
        return (total_overtime_hours, Decimal('0.0'))
    else:
        # 2 primeiras horas são 50%, restante é 100%
        return (Decimal('2.0'), total_overtime_hours - Decimal('2.0'))

# Função para simular o cálculo de interjornada
def test_interjornada(prev_exit_time, next_entry_time):
    """
    Calcula as horas faltantes de interjornada
    
    Args:
        prev_exit_time: Horário de saída do dia anterior (string no formato HH:MM)
        next_entry_time: Horário de entrada do dia atual (string no formato HH:MM)
        
    Returns:
        Horas faltantes de interjornada (se houver)
    """
    # Converter para objetos time
    prev_exit = str_to_time(prev_exit_time)
    next_entry = str_to_time(next_entry_time)
    
    # Calcular intervalo em horas
    prev_exit_dt = datetime.combine(date.today(), prev_exit)
    next_entry_dt = datetime.combine(date.today() + timedelta(days=1), next_entry)
    
    interjornada_seconds = (next_entry_dt - prev_exit_dt).total_seconds()
    interjornada_hours = interjornada_seconds / 3600
    
    # Verificar se há violação de interjornada (menos de 11 horas)
    interjornada_hours_required = 11
    
    if interjornada_hours < interjornada_hours_required:
        # Calcular horas faltantes
        missing_hours = interjornada_hours_required - interjornada_hours
        return Decimal(str(missing_hours)).quantize(Decimal('0.01'))
    
    return Decimal('0.0')

# Testes
def run_tests():
    print("=== TESTES DA NOVA REGRA DE CÁLCULO DE HORAS EXTRAS ===")
    print("Regra da convenção coletiva:")
    print("- As 2 primeiras horas extras do dia são pagas a 50%")
    print("- As demais horas extras são pagas a 100%")
    print("- Horas de interjornada são somadas às horas extras do dia")
    print("\n")
    
    # Teste 1: Dia normal com 10 horas trabalhadas (8 regulares + 2 extras)
    periods1 = [
        MockPeriod(
            'regular',
            str_to_time('09:00'),
            str_to_time('12:00'),
            str_to_time('13:00'),
            str_to_time('20:00')
        )
    ]
    
    regular1, overtime1, night1 = test_calculate_day_hours(periods1)
    ot50_1, ot100_1 = apply_overtime_convention_rule(overtime1)
    
    print("=== Teste 1: Dia normal com 10 horas trabalhadas ===")
    print(f"Horas regulares: {regular1}")
    print(f"Horas extras totais: {overtime1}")
    print(f"Horas extras 50%: {ot50_1}")
    print(f"Horas extras 100%: {ot100_1}")
    print(f"Horas noturnas: {night1}")
    print("Esperado: 8 horas regulares, 2 horas extras 50%, 0 horas extras 100%")
    print("\n")
    
    # Teste 2: Dia normal com 12 horas trabalhadas (8 regulares + 4 extras)
    periods2 = [
        MockPeriod(
            'regular',
            str_to_time('09:00'),
            str_to_time('12:00'),
            str_to_time('13:00'),
            str_to_time('22:00')
        )
    ]
    
    regular2, overtime2, night2 = test_calculate_day_hours(periods2)
    ot50_2, ot100_2 = apply_overtime_convention_rule(overtime2)
    
    print("=== Teste 2: Dia normal com 12 horas trabalhadas ===")
    print(f"Horas regulares: {regular2}")
    print(f"Horas extras totais: {overtime2}")
    print(f"Horas extras 50%: {ot50_2}")
    print(f"Horas extras 100%: {ot100_2}")
    print(f"Horas noturnas: {night2}")
    print("Esperado: 8 horas regulares, 2 horas extras 50%, 2 horas extras 100%")
    print("\n")
    
    # Teste 3: Fim de semana com 6 horas trabalhadas (todas extras)
    periods3 = [
        MockPeriod(
            'regular',
            str_to_time('10:00'),
            str_to_time('13:00'),
            str_to_time('14:00'),
            str_to_time('17:00')
        )
    ]
    
    regular3, overtime3, night3 = test_calculate_day_hours(periods3, is_weekend_or_holiday=True)
    ot50_3, ot100_3 = apply_overtime_convention_rule(overtime3)
    
    print("=== Teste 3: Fim de semana com 6 horas trabalhadas ===")
    print(f"Horas regulares: {regular3}")
    print(f"Horas extras totais: {overtime3}")
    print(f"Horas extras 50%: {ot50_3}")
    print(f"Horas extras 100%: {ot100_3}")
    print(f"Horas noturnas: {night3}")
    print("Esperado: 0 horas regulares, 2 horas extras 50%, 4 horas extras 100%")
    print("\n")
    
    # Teste 4: Dia com múltiplos períodos
    periods4 = [
        MockPeriod(
            'regular',
            str_to_time('09:00'),
            str_to_time('12:00'),
            str_to_time('13:00'),
            str_to_time('18:00')
        ),
        MockPeriod(
            'additional',
            str_to_time('20:00'),
            None,
            None,
            str_to_time('23:00')
        )
    ]
    
    regular4, overtime4, night4 = test_calculate_day_hours(periods4)
    ot50_4, ot100_4 = apply_overtime_convention_rule(overtime4)
    
    print("=== Teste 4: Dia com múltiplos períodos ===")
    print(f"Horas regulares: {regular4}")
    print(f"Horas extras totais: {overtime4}")
    print(f"Horas extras 50%: {ot50_4}")
    print(f"Horas extras 100%: {ot100_4}")
    print(f"Horas noturnas: {night4}")
    print("Esperado: 8 horas regulares, 2 horas extras 50%, 1 hora extra 100%, 1 hora noturna")
    print("\n")
    
    # Teste 5: Interjornada
    interjornada_hours = test_interjornada('18:00', '03:00')
    
    print("=== Teste 5: Cálculo de Interjornada ===")
    print(f"Saída do dia anterior: 18:00")
    print(f"Entrada do dia atual: 03:00")
    print(f"Horas faltantes de interjornada: {interjornada_hours}")
    print("Esperado: 5 horas faltantes (11h requeridas - 6h concedidas)")
    print("\n")
    
    # Teste 6: Dia com horas extras + interjornada
    periods6 = [
        MockPeriod(
            'regular',
            str_to_time('09:00'),
            str_to_time('12:00'),
            str_to_time('13:00'),
            str_to_time('19:00')
        )
    ]
    
    regular6, overtime6, night6 = test_calculate_day_hours(periods6)
    
    # Adicionar horas de interjornada às horas extras
    interjornada_hours6 = test_interjornada('19:00', '03:00')
    total_overtime6 = overtime6 + interjornada_hours6
    
    # Aplicar regra da convenção
    ot50_6, ot100_6 = apply_overtime_convention_rule(total_overtime6)
    
    print("=== Teste 6: Dia com horas extras + interjornada ===")
    print(f"Horas regulares: {regular6}")
    print(f"Horas extras normais: {overtime6}")
    print(f"Horas faltantes de interjornada: {interjornada_hours6}")
    print(f"Total de horas extras: {total_overtime6}")
    print(f"Horas extras 50%: {ot50_6}")
    print(f"Horas extras 100%: {ot100_6}")
    print("Esperado: 8 horas regulares, 1 hora extra normal, 5 horas de interjornada")
    print("          Total: 6 horas extras (2h a 50%, 4h a 100%)")
    print("\n")
    
    print("Testes concluídos!")

# Executar os testes
if __name__ == "__main__":
    run_tests()
