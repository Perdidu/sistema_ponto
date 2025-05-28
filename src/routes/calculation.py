from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date, timedelta
from src.models import db, Employee, WorkDay, WorkPeriod, Calculation
from src.utils.calculation_utils import calculate_multiple_periods, calculate_period_hours, is_weekend, is_holiday
import traceback
from decimal import Decimal

calculation_bp = Blueprint('calculation', __name__)

@calculation_bp.route('/calculations', methods=['GET'])
def list_calculations():
    employee_id = request.args.get('employee_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Definir período padrão se não for especificado
    if not start_date:
        today = date.today()
        start_date = date(today.year, today.month, 1).isoformat()
    
    if not end_date:
        today = date.today()
        if today.month == 12:
            end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)
        end_date = end_date.isoformat()
    
    # Converter strings para objetos date
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Buscar cálculos existentes
    query = Calculation.query
    
    if employee_id:
        query = query.filter(Calculation.employee_id == employee_id)
    
    # Filtrar por período personalizado
    query = query.filter(
        Calculation.period_start >= start_date_obj,
        Calculation.period_end <= end_date_obj
    )
    
    calculations = query.order_by(Calculation.period_start.desc()).all()
    
    # Se não houver cálculos existentes, mas houver registros de ponto, calcular automaticamente
    if not calculations and employee_id:
        # Verificar se existem registros de ponto para o período
        work_days = WorkDay.query.filter(
            WorkDay.employee_id == employee_id,
            WorkDay.date >= start_date_obj,
            WorkDay.date <= end_date_obj
        ).all()
        
        if work_days:
            # Há registros de ponto, mas não há cálculo - criar um cálculo temporário
            calculation_results = calculate_multiple_periods(employee_id, start_date_obj, end_date_obj)
            
            # Criar um objeto de cálculo temporário (não salvar no banco)
            temp_calculation = Calculation(
                id=0,  # ID temporário
                employee_id=employee_id,
                period_start=start_date_obj,
                period_end=end_date_obj,
                regular_hours=calculation_results['regular_hours'],
                overtime_50=calculation_results['overtime_50'],
                overtime_100=calculation_results['overtime_100'],
                night_hours=calculation_results['night_hours'],
                interjournada_hours=calculation_results['interjournada_hours'],
                overtime_50_value=calculation_results['overtime_50_value'],
                overtime_100_value=calculation_results['overtime_100_value'],
                night_hours_value=calculation_results['night_hours_value'],
                interjournada_value=calculation_results['interjournada_value'],
                dsr_value=calculation_results['dsr_value'],
                total_value=calculation_results['total_value']
            )
            
            # Buscar o funcionário para associar ao cálculo temporário
            employee = Employee.query.get(employee_id)
            temp_calculation.employee = employee
            
            # Adicionar o cálculo temporário à lista
            calculations = [temp_calculation]
    
    employees = Employee.query.all()
    
    return render_template('calculations/index.html', 
                          calculations=calculations, 
                          employees=employees,
                          employee_id=employee_id,
                          start_date=start_date,
                          end_date=end_date)

@calculation_bp.route('/calculations/new', methods=['GET'])
def new_calculation():
    employees = Employee.query.all()
    
    # Definir período padrão (mês atual)
    today = date.today()
    start_date = date(today.year, today.month, 1)
    if today.month == 12:
        end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)
    
    return render_template('calculations/new.html', 
                          employees=employees, 
                          start_date=start_date.isoformat(),
                          end_date=end_date.isoformat())

@calculation_bp.route('/calculations', methods=['POST'])
def create_calculation():
    try:
        employee_id = request.form['employee_id']
        period_start = datetime.strptime(request.form['period_start'], '%Y-%m-%d').date()
        period_end = datetime.strptime(request.form['period_end'], '%Y-%m-%d').date()
        
        # Verificar se já existe cálculo para este funcionário neste período
        existing_calculation = Calculation.query.filter_by(
            employee_id=employee_id,
            period_start=period_start,
            period_end=period_end
        ).first()
        
        if existing_calculation:
            flash('Já existe um cálculo para este funcionário neste período. Visualize o cálculo existente.', 'danger')
            return redirect(url_for('calculation.show_calculation', id=existing_calculation.id))
        
        # Verificar se existem registros de ponto para o período
        work_days = WorkDay.query.filter(
            WorkDay.employee_id == employee_id,
            WorkDay.date >= period_start,
            WorkDay.date <= period_end
        ).all()
        
        if not work_days:
            flash('Não há registros de ponto para este funcionário neste período.', 'warning')
            return redirect(url_for('calculation.new_calculation'))
        
        # Realizar cálculo com base nos registros de ponto
        calculation_results = calculate_multiple_periods(employee_id, period_start, period_end)
        
        # Criar novo cálculo
        calculation = Calculation(
            employee_id=employee_id,
            period_start=period_start,
            period_end=period_end,
            regular_hours=calculation_results['regular_hours'],
            overtime_50=calculation_results['overtime_50'],
            overtime_100=calculation_results['overtime_100'],
            night_hours=calculation_results['night_hours'],
            interjournada_hours=calculation_results['interjournada_hours'],
            overtime_50_value=calculation_results['overtime_50_value'],
            overtime_100_value=calculation_results['overtime_100_value'],
            night_hours_value=calculation_results['night_hours_value'],
            interjournada_value=calculation_results['interjournada_value'],
            dsr_value=calculation_results['dsr_value'],
            total_value=calculation_results['total_value']
        )
        
        db.session.add(calculation)
        db.session.commit()
        
        flash('Cálculo realizado com sucesso!', 'success')
        return redirect(url_for('calculation.show_calculation', id=calculation.id))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao realizar cálculo: {str(e)}', 'danger')
        return redirect(url_for('calculation.new_calculation'))

@calculation_bp.route('/calculations/<int:id>', methods=['GET'])
def show_calculation(id):
    calculation = Calculation.query.get_or_404(id)
    return render_template('calculations/show.html', calculation=calculation)

@calculation_bp.route('/calculations/<int:id>/detailed', methods=['GET'])
def detailed_calculation(id):
    calculation = Calculation.query.get_or_404(id)
    
    # Buscar todos os dias de trabalho no período
    work_days = WorkDay.query.filter(
        WorkDay.employee_id == calculation.employee_id,
        WorkDay.date >= calculation.period_start,
        WorkDay.date <= calculation.period_end
    ).order_by(WorkDay.date).all()
    
    # Preparar detalhamento diário
    daily_details = []
    
    # Mapear dias da semana em português
    weekday_names = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
    
    # Variáveis para controle de interjornada
    prev_exit_time = None
    prev_date = None
    
    # Para cada dia no período
    current_date = calculation.period_start
    while current_date <= calculation.period_end:
        # Buscar o registro de trabalho para este dia
        work_day = next((wd for wd in work_days if wd.date == current_date), None)
        
        # Se houver registro para este dia
        if work_day and work_day.work_periods:
            # Calcular horas do dia
            day_regular, day_overtime, day_night = calculate_period_hours(
                work_day.work_periods, current_date, calculation.employee
            )
            
            # Aplicar regra da convenção: 2 primeiras horas como 50%, demais como 100%
            if day_overtime <= 2.0:
                # Todas as horas extras são 50%
                day_ot50 = day_overtime
                day_ot100 = 0.0
            else:
                # 2 primeiras horas são 50%, restante é 100%
                day_ot50 = 2.0
                day_ot100 = day_overtime - 2.0
            
            # Calcular interjornada
            interjournada_hours = 0
            
            # Encontrar o último horário de saída do dia
            last_exit_time = None
            for period in work_day.work_periods:
                if period.exit_time:
                    if last_exit_time is None or period.exit_time > last_exit_time:
                        last_exit_time = period.exit_time
            
            # Se tiver saída hoje e entrada ontem
            if prev_exit_time and prev_date:
                # Encontrar o primeiro horário de entrada do dia
                first_entry_time = None
                for period in work_day.work_periods:
                    if period.entry_time:
                        if first_entry_time is None or period.entry_time < first_entry_time:
                            first_entry_time = period.entry_time
                
                if first_entry_time and last_exit_time:
                    # Se for dia seguinte
                    if (current_date - prev_date).days == 1:
                        prev_exit_dt = datetime.combine(prev_date, prev_exit_time)
                        current_entry_dt = datetime.combine(current_date, first_entry_time)
                        
                        interjornada_seconds = (current_entry_dt - prev_exit_dt).total_seconds()
                        interjornada_hours_required = 11 * 3600  # 11 horas em segundos
                        
                        if interjornada_seconds < interjornada_hours_required:
                            # Calcular horas faltantes de interjornada
                            missing_hours = (interjornada_hours_required - interjornada_seconds) / 3600
                            interjournada_hours = missing_hours
            
            # Adicionar detalhes do dia
            daily_details.append({
                'date': current_date,
                'weekday': weekday_names[current_date.weekday()],
                'regular_hours': day_regular,
                'overtime_50': day_ot50,
                'overtime_100': day_ot100,
                'night_hours': day_night,
                'interjournada_hours': interjournada_hours
            })
            
            # Atualizar para próxima iteração
            prev_exit_time = last_exit_time
            prev_date = current_date
        else:
            # Dia sem registro
            daily_details.append({
                'date': current_date,
                'weekday': weekday_names[current_date.weekday()],
                'regular_hours': 0,
                'overtime_50': 0,
                'overtime_100': 0,
                'night_hours': 0,
                'interjournada_hours': 0
            })
        
        # Avançar para o próximo dia
        current_date += timedelta(days=1)
    
    return render_template('calculations/detailed.html', 
                          calculation=calculation,
                          daily_details=daily_details)

@calculation_bp.route('/detailed-calculations', methods=['GET'])
def detailed_calculations():
    try:
        # Inicializar valores padrão
        employee_id = request.args.get('employee_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Definir período padrão se não for especificado
        today = date.today()
        if not start_date:
            start_date = date(today.year, today.month, 1).isoformat()
        
        if not end_date:
            if today.month == 12:
                end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)
            end_date = end_date.isoformat()
        
        # Converter strings para objetos date com tratamento de erro
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError as e:
            flash(f'Erro no formato de data: {str(e)}. Use o formato YYYY-MM-DD.', 'danger')
            start_date_obj = date(today.year, today.month, 1)
            end_date_obj = date(today.year, today.month + 1, 1) - timedelta(days=1)
            start_date = start_date_obj.isoformat()
            end_date = end_date_obj.isoformat()
        
        # Buscar funcionários
        employees = Employee.query.all()
        
        # Inicializar listas e totais
        daily_details = []
        totals = {
            'regular_hours': 0,
            'overtime_50': 0,
            'overtime_100': 0,
            'night_hours': 0,
            'interjournada_hours': 0,
            'overtime_50_value': 0,
            'overtime_100_value': 0,
            'night_hours_value': 0,
            'interjournada_value': 0,
            'dsr_value': 0,
            'total_value': 0
        }
        
        # Mapear dias da semana em português
        weekday_names = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
        
        # Se um funcionário específico for selecionado
        if employee_id:
            employee = Employee.query.get(employee_id)
            if employee:
                employee_list = [employee]
            else:
                employee_list = []
        else:
            employee_list = employees
        
        # Para cada funcionário
        for employee in employee_list:
            # Buscar todos os dias de trabalho no período
            work_days = WorkDay.query.filter(
                WorkDay.employee_id == employee.id,
                WorkDay.date >= start_date_obj,
                WorkDay.date <= end_date_obj
            ).order_by(WorkDay.date).all()
            
            # Variáveis para controle de interjornada
            prev_exit_time = None
            prev_date = None
            
            # Para cada dia no período
            current_date = start_date_obj
            while current_date <= end_date_obj:
                # Buscar o registro de trabalho para este dia
                work_day = next((wd for wd in work_days if wd.date == current_date), None)
                
                # Se houver registro para este dia
                if work_day and work_day.work_periods:
                    # Calcular horas do dia
                    day_regular, day_overtime, day_night = calculate_period_hours(
                        work_day.work_periods, current_date, employee
                    )
                    
                    # Aplicar regra da convenção: 2 primeiras horas como 50%, demais como 100%
                    # Converter para Decimal para evitar erro de tipo
                    from decimal import Decimal
                    day_overtime_decimal = Decimal(str(day_overtime))
                    
                    if day_overtime_decimal <= Decimal('2.0'):
                        # Todas as horas extras são 50%
                        day_ot50 = day_overtime_decimal
                        day_ot100 = Decimal('0.0')
                    else:
                        # 2 primeiras horas são 50%, restante é 100%
                        day_ot50 = Decimal('2.0')
                        day_ot100 = day_overtime_decimal - Decimal('2.0')
                    
                    # Calcular interjornada
                    interjournada_hours = 0
                    
                    # Encontrar o último horário de saída do dia
                    last_exit_time = None
                    for period in work_day.work_periods:
                        if period.exit_time:
                            if last_exit_time is None or period.exit_time > last_exit_time:
                                last_exit_time = period.exit_time
                    
                    # Se tiver saída hoje e entrada ontem
                    if prev_exit_time and prev_date:
                        # Encontrar o primeiro horário de entrada do dia
                        first_entry_time = None
                        for period in work_day.work_periods:
                            if period.entry_time:
                                if first_entry_time is None or period.entry_time < first_entry_time:
                                    first_entry_time = period.entry_time
                        
                        if first_entry_time and last_exit_time:
                            # Se for dia seguinte
                            if (current_date - prev_date).days == 1:
                                prev_exit_dt = datetime.combine(prev_date, prev_exit_time)
                                current_entry_dt = datetime.combine(current_date, first_entry_time)
                                
                                interjornada_seconds = (current_entry_dt - prev_exit_dt).total_seconds()
                                interjornada_hours_required = 11 * 3600  # 11 horas em segundos
                                
                                if interjornada_seconds < interjornada_hours_required:
                                    # Calcular horas faltantes de interjornada
                                    missing_hours = (interjornada_hours_required - interjornada_seconds) / 3600
                                    interjournada_hours = missing_hours
                    
                    # Adicionar detalhes do dia
                    daily_details.append({
                        'date': current_date,
                        'weekday': weekday_names[current_date.weekday()],
                        'employee_name': employee.name,
                        'regular_hours': day_regular,
                        'overtime_50': day_ot50,
                        'overtime_100': day_ot100,
                        'night_hours': day_night,
                        'interjournada_hours': interjournada_hours
                    })
                    
                    # Atualizar totais
                    totals['regular_hours'] += day_regular
                    totals['overtime_50'] += day_ot50
                    totals['overtime_100'] += day_ot100
                    totals['night_hours'] += day_night
                    totals['interjournada_hours'] += interjournada_hours
                    
                    # Atualizar para próxima iteração
                    prev_exit_time = last_exit_time
                    prev_date = current_date
                else:
                    # Dia sem registro, só adicionar se um funcionário específico for selecionado
                    if employee_id:
                        daily_details.append({
                            'date': current_date,
                            'weekday': weekday_names[current_date.weekday()],
                            'employee_name': employee.name,
                            'regular_hours': 0,
                            'overtime_50': 0,
                            'overtime_100': 0,
                            'night_hours': 0,
                            'interjournada_hours': 0
                        })
                
                # Avançar para o próximo dia
                current_date += timedelta(days=1)
        
        # Calcular valores financeiros
        if employee_id:
            employee = Employee.query.get(employee_id)
            if employee and employee.salary:
                # Converter salary para float para evitar problemas de tipo
                hourly_rate = float(employee.salary) / 220.0  # Valor da hora normal (220h mensais)
                
                # Garantir que todos os valores sejam float
                totals['overtime_50_value'] = float(totals['overtime_50']) * hourly_rate * 1.5
                totals['overtime_100_value'] = float(totals['overtime_100']) * hourly_rate * 2.0
                totals['night_hours_value'] = float(totals['night_hours']) * hourly_rate * 0.2
                totals['interjournada_value'] = float(totals['interjournada_hours']) * hourly_rate * 1.5
                
                # Calcular DSR sobre horas extras
                total_work_days = len([d for d in daily_details if d['regular_hours'] > 0 or d['overtime_50'] > 0 or d['overtime_100'] > 0])
                if total_work_days > 0:
                    # Considerar domingos e feriados como dias de descanso
                    total_rest_days = len([d for d in daily_details if d['weekday'] == 'Domingo'])
                    
                    if total_rest_days > 0:
                        total_overtime_value = totals['overtime_50_value'] + totals['overtime_100_value']
                        totals['dsr_value'] = (total_overtime_value / total_work_days) * total_rest_days
                
                totals['total_value'] = (
                    totals['overtime_50_value'] + 
                    totals['overtime_100_value'] + 
                    totals['night_hours_value'] + 
                    totals['interjournada_value'] + 
                    totals['dsr_value']
                )
        
        return render_template('calculations/detailed_tab.html', 
                            employees=employees,
                            employee_id=employee_id,
                            start_date=start_date,
                            end_date=end_date,
                            daily_details=daily_details,
                            totals=totals)
    
    except Exception as e:
        # Capturar e logar o erro detalhado
        error_details = traceback.format_exc()
        print(f"ERRO NA PÁGINA DE CÁLCULO DETALHADO: {error_details}")
        
        # Retornar para o usuário com mensagem de erro
        flash(f'Erro ao processar cálculo detalhado: {str(e)}', 'danger')
        
        # Buscar funcionários para o template
        employees = Employee.query.all()
        
        # Definir valores padrão para evitar erros no template
        today = date.today()
        start_date = date(today.year, today.month, 1).isoformat()
        end_date = (date(today.year, today.month + 1, 1) - timedelta(days=1)).isoformat()
        
        # Retornar template com valores vazios
        return render_template('calculations/detailed_tab.html', 
                            employees=employees,
                            employee_id=employee_id if 'employee_id' in locals() else None,
                            start_date=start_date,
                            end_date=end_date,
                            daily_details=[],
                            totals={
                                'regular_hours': 0,
                                'overtime_50': 0,
                                'overtime_100': 0,
                                'night_hours': 0,
                                'interjournada_hours': 0,
                                'overtime_50_value': 0,
                                'overtime_100_value': 0,
                                'night_hours_value': 0,
                                'interjournada_value': 0,
                                'dsr_value': 0,
                                'total_value': 0
                            })

@calculation_bp.route('/calculations/<int:id>/delete', methods=['POST'])
def delete_calculation(id):
    calculation = Calculation.query.get_or_404(id)
    
    try:
        db.session.delete(calculation)
        db.session.commit()
        
        flash('Cálculo excluído com sucesso!', 'success')
        return redirect(url_for('calculation.list_calculations'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir cálculo: {str(e)}', 'danger')
        return redirect(url_for('calculation.list_calculations'))
