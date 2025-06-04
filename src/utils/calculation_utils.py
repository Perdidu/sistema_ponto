from datetime import datetime, date, timedelta
from decimal import Decimal
from src.models import db, Calculation, Employee, Holiday, WorkDay, WorkPeriod
import calendar

def calculate_hours_difference(start_time, end_time):
    """Calcula a diferença em horas entre dois horários"""
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

def is_night_time(time_obj):
    """Verifica se o horário está no período noturno (22h às 5h)"""
    night_start = datetime.strptime('22:00', '%H:%M').time()
    night_end = datetime.strptime('05:00', '%H:%M').time()
    
    if night_start <= time_obj or time_obj <= night_end:
        return True
    return False

def calculate_night_hours(start_time, end_time):
    """Calcula as horas noturnas entre dois horários"""
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

def is_holiday(check_date):
    """Verifica se a data é um feriado"""
    return Holiday.query.filter_by(date=check_date).first() is not None

def is_weekend(check_date):
    """Verifica se a data é um fim de semana (sábado ou domingo)"""
    return check_date.weekday() >= 5  # 5 = sábado, 6 = domingo

def calculate_dsr(overtime_50_value, overtime_100_value, workdays, total_days):
    """Calcula o DSR sobre as horas extras"""
    if workdays == 0:
        return Decimal('0.0')
    
    total_overtime = overtime_50_value + overtime_100_value
    dsr_days = total_days - workdays
    
    if dsr_days <= 0:
        return Decimal('0.0')
    
    dsr_value = (total_overtime / Decimal(str(workdays))) * Decimal(str(dsr_days))
    return dsr_value.quantize(Decimal('0.01'))

def calculate_period_hours(periods, current_date, employee):
    """
    Calcula as horas trabalhadas em todos os períodos de um dia
    
    Args:
        periods: Lista de períodos de trabalho do dia
        current_date: Data atual sendo processada
        employee: Objeto do funcionário
        
    Returns:
        Tupla com (horas_regulares, horas_extras_total, horas_noturnas)
    """
    # Inicializar contadores
    regular_hours = Decimal('0.0')
    overtime_hours = Decimal('0.0')
    night_hours = Decimal('0.0')
    
    # Horas regulares máximas por dia
    workday_hours = Decimal('8.0')  # 8 horas por dia
    
    # Verificar se é dia útil ou não
    is_workday = not is_weekend(current_date) and not is_holiday(current_date)
    
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
        if is_workday:
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

def calculate_multiple_periods(employee_id, period_start, period_end):
    """
    Calcula horas trabalhadas considerando múltiplos períodos por dia
    
    Args:
        employee_id: ID do funcionário
        period_start: Data inicial do período
        period_end: Data final do período
        
    Returns:
        Dicionário com os resultados dos cálculos
    """
    # Buscar funcionário
    employee = Employee.query.get_or_404(employee_id)
    
    # Inicializar variáveis para cálculo
    regular_hours = Decimal('0.0')
    overtime_50 = Decimal('0.0')
    overtime_100 = Decimal('0.0')
    night_hours = Decimal('0.0')
    interjournada_hours = Decimal('0.0')
    
    # Calcular horas trabalhadas por dia
    prev_exit_time = None
    prev_date = None
    workdays = 0
    
    # Dicionário para armazenar detalhes diários para relatório
    daily_details = {}
    
    # Para cada dia no período
    current_date = period_start
    while current_date <= period_end:
        # Inicializar detalhes do dia
        daily_details[current_date] = {
            'regular_hours': Decimal('0.0'),
            'overtime_50': Decimal('0.0'),
            'overtime_100': Decimal('0.0'),
            'night_hours': Decimal('0.0'),
            'interjournada_hours': Decimal('0.0'),
            'total_overtime_hours': Decimal('0.0'),
            'is_weekend': is_weekend(current_date),
            'is_holiday': is_holiday(current_date)
        }
        
        # Verificar se é dia útil para contagem de DSR
        if not is_weekend(current_date) and not is_holiday(current_date):
            workdays += 1
        
        # Buscar todos os períodos do dia
        work_day = WorkDay.query.filter_by(
            employee_id=employee_id,
            date=current_date
        ).first()
        
        # Se houver registros neste dia
        if work_day and work_day.work_periods:
            # Calcular horas do dia
            day_regular, day_overtime, day_night = calculate_period_hours(
                work_day.work_periods, current_date, employee
            )
            
            # Armazenar horas regulares e noturnas
            regular_hours += day_regular
            night_hours += day_night
            
            # Verificar interjornada (11 horas entre jornadas)
            day_interjornada = Decimal('0.0')
            
            # Encontrar o último horário de saída do dia anterior
            if prev_exit_time and prev_date:
                # Encontrar o primeiro horário de entrada do dia atual
                first_entry_time = None
                for period in work_day.work_periods:
                    if period.entry_time:
                        if first_entry_time is None or period.entry_time < first_entry_time:
                            first_entry_time = period.entry_time
                
                if first_entry_time:
                    # Calcular tempo entre jornadas
                    prev_exit_dt = datetime.combine(prev_date, prev_exit_time)
                    current_entry_dt = datetime.combine(current_date, first_entry_time)
                    
                    # Verificar se o intervalo é ininterrupto (conforme CLT e jurisprudência)
                    if (current_date - prev_date).days == 1:
                        interjornada_seconds = (current_entry_dt - prev_exit_dt).total_seconds()
                        interjornada_hours_required = 11 * 3600  # 11 horas em segundos
                        
                        if interjornada_seconds < interjornada_hours_required:
                            # Calcular horas faltantes de interjornada
                            missing_hours = (interjornada_hours_required - interjornada_seconds) / 3600
                            day_interjornada = Decimal(str(missing_hours)).quantize(Decimal('0.01'))
                            interjournada_hours += day_interjornada
            
            # Armazenar detalhes da interjornada para o dia atual
            daily_details[current_date]['interjournada_hours'] = day_interjornada
            
            # Total de horas extras do dia (incluindo interjornada)
            total_day_overtime = day_overtime + day_interjornada
            daily_details[current_date]['total_overtime_hours'] = total_day_overtime
            
            # Aplicar regra da convenção: 2 primeiras horas como 50%, demais como 100%
            if total_day_overtime <= Decimal('2.0'):
                # Todas as horas extras são 50%
                day_ot50 = total_day_overtime
                day_ot100 = Decimal('0.0')
            else:
                # 2 primeiras horas são 50%, restante é 100%
                day_ot50 = Decimal('2.0')
                day_ot100 = total_day_overtime - Decimal('2.0')
            
            # Acumular horas extras
            overtime_50 += day_ot50
            overtime_100 += day_ot100
            
            # Armazenar detalhes do dia
            daily_details[current_date]['regular_hours'] = day_regular
            daily_details[current_date]['overtime_50'] = day_ot50
            daily_details[current_date]['overtime_100'] = day_ot100
            daily_details[current_date]['night_hours'] = day_night
            
            # Encontrar o último horário de saída do dia atual para próxima iteração
            last_exit_time = None
            for period in work_day.work_periods:
                if period.exit_time:
                    if last_exit_time is None or period.exit_time > last_exit_time:
                        last_exit_time = period.exit_time
            
            # Atualizar para próxima iteração
            prev_exit_time = last_exit_time
            prev_date = current_date
        
        # Avançar para o próximo dia
        current_date += timedelta(days=1)
    
    # Calcular valores financeiros
    hourly_rate = employee.salary / Decimal('220')  # 220 horas mensais (padrão CLT)
    
    overtime_50_value = overtime_50 * hourly_rate * Decimal('1.5')
    overtime_100_value = overtime_100 * hourly_rate * Decimal('2.0')
    night_hours_value = night_hours * hourly_rate * Decimal('0.2')  # 20% adicional noturno
    interjournada_value = interjournada_hours * hourly_rate * Decimal('1.5')
    
    # Calcular DSR sobre horas extras
    total_days = (period_end - period_start).days + 1
    dsr_value = calculate_dsr(overtime_50_value, overtime_100_value, workdays, total_days)
    
    # Calcular valor total
    total_value = overtime_50_value + overtime_100_value + night_hours_value + interjournada_value + dsr_value
    
    # Retornar resultados
    return {
        'regular_hours': float(regular_hours),
        'overtime_50': float(overtime_50),
        'overtime_100': float(overtime_100),
        'night_hours': float(night_hours),
        'interjournada_hours': float(interjournada_hours),
        'interjournada_value': float(interjournada_value),
        'overtime_50_value': float(overtime_50_value),
        'overtime_100_value': float(overtime_100_value),
        'night_hours_value': float(night_hours_value),
        'dsr_value': float(dsr_value),
        'total_value': float(total_value),
        'daily_details': daily_details
    }
