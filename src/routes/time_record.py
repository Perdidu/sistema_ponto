from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date, timedelta
from src.models import db, Employee, WorkDay, WorkPeriod

time_record_bp = Blueprint('time_record', __name__)

@time_record_bp.route('/time_records', methods=['GET'])
def list_time_records():
    employee_id = request.args.get('employee_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = WorkDay.query
    
    if employee_id:
        query = query.filter(WorkDay.employee_id == employee_id)
    
    if start_date:
        query = query.filter(WorkDay.date >= start_date)
    
    if end_date:
        query = query.filter(WorkDay.date <= end_date)
    
    work_days = query.order_by(WorkDay.date.desc()).all()
    employees = Employee.query.all()
    
    return render_template('time_records/index.html', 
                          work_days=work_days, 
                          employees=employees,
                          employee_id=employee_id,
                          start_date=start_date,
                          end_date=end_date)

@time_record_bp.route('/time_records/new', methods=['GET'])
def new_time_record():
    employees = Employee.query.all()
    today = date.today().isoformat()
    return render_template('time_records/new.html', employees=employees, today=today)

@time_record_bp.route('/time_records', methods=['POST'])
def create_time_record():
    try:
        employee_id = request.form['employee_id']
        record_date = request.form['date']
        notes = request.form.get('notes')
        
        # Verificar se já existe registro para este funcionário nesta data
        existing_work_day = WorkDay.query.filter_by(
            employee_id=employee_id,
            date=record_date
        ).first()
        
        if existing_work_day:
            flash('Já existe um registro para este funcionário nesta data. Edite o registro existente.', 'danger')
            return redirect(url_for('time_record.edit_time_record', id=existing_work_day.id))
        
        # Criar o dia de trabalho
        work_day = WorkDay(
            employee_id=employee_id,
            date=record_date,
            notes=notes
        )
        
        db.session.add(work_day)
        db.session.flush()  # Para obter o ID do work_day
        
        # Processar os períodos
        period_keys = [k for k in request.form.keys() if k.startswith('periods[') and k.endswith('][period_type]')]
        
        for key in period_keys:
            # Extrair o índice do período do nome do campo
            index = key.split('[')[1].split(']')[0]
            
            period_type = request.form.get(f'periods[{index}][period_type]')
            entry_time = request.form.get(f'periods[{index}][entry_time]')
            exit_time = request.form.get(f'periods[{index}][exit_time]')
            
            # Verificar se os horários foram preenchidos
            if not entry_time and not exit_time:
                continue
            
            # Criar o período de trabalho com tratamento seguro para todos os campos
            work_period = WorkPeriod(
                work_day_id=work_day.id,
                period_type=period_type,
                entry_time=entry_time if entry_time else None,
                exit_time=exit_time if exit_time else None
            )
            
            # Adicionar campos de almoço apenas se for período regular e os campos não estiverem vazios
            if period_type == 'regular':
                lunch_start = request.form.get(f'periods[{index}][lunch_start]')
                lunch_end = request.form.get(f'periods[{index}][lunch_end]')
                
                if lunch_start and lunch_start.strip():
                    work_period.lunch_start = lunch_start
                
                if lunch_end and lunch_end.strip():
                    work_period.lunch_end = lunch_end
            
            db.session.add(work_period)
        
        db.session.commit()
        
        flash('Registro de ponto criado com sucesso!', 'success')
        return redirect(url_for('time_record.list_time_records'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar registro de ponto: {str(e)}', 'danger')
        return redirect(url_for('time_record.new_time_record'))

@time_record_bp.route('/time_records/<int:id>', methods=['GET'])
def show_time_record(id):
    work_day = WorkDay.query.get_or_404(id)
    return render_template('time_records/show.html', work_day=work_day)

@time_record_bp.route('/time_records/<int:id>/edit', methods=['GET'])
def edit_time_record(id):
    work_day = WorkDay.query.get_or_404(id)
    employees = Employee.query.all()
    return render_template('time_records/edit.html', work_day=work_day, employees=employees)

@time_record_bp.route('/time_records/<int:id>', methods=['POST'])
def update_time_record(id):
    work_day = WorkDay.query.get_or_404(id)
    
    try:
        work_day.employee_id = request.form['employee_id']
        work_day.date = request.form['date']
        work_day.notes = request.form.get('notes')
        
        # Remover todos os períodos existentes
        for period in work_day.work_periods:
            db.session.delete(period)
        
        # Processar os períodos
        period_keys = [k for k in request.form.keys() if k.startswith('periods[') and k.endswith('][period_type]')]
        
        for key in period_keys:
            # Extrair o índice do período do nome do campo
            index = key.split('[')[1].split(']')[0]
            
            period_type = request.form.get(f'periods[{index}][period_type]')
            entry_time = request.form.get(f'periods[{index}][entry_time]')
            exit_time = request.form.get(f'periods[{index}][exit_time]')
            
            # Verificar se os horários foram preenchidos
            if not entry_time and not exit_time:
                continue
            
            # Criar o período de trabalho com tratamento seguro para todos os campos
            work_period = WorkPeriod(
                work_day_id=work_day.id,
                period_type=period_type,
                entry_time=entry_time if entry_time else None,
                exit_time=exit_time if exit_time else None
            )
            
            # Adicionar campos de almoço apenas se for período regular e os campos não estiverem vazios
            if period_type == 'regular':
                lunch_start = request.form.get(f'periods[{index}][lunch_start]')
                lunch_end = request.form.get(f'periods[{index}][lunch_end]')
                
                if lunch_start and lunch_start.strip():
                    work_period.lunch_start = lunch_start
                
                if lunch_end and lunch_end.strip():
                    work_period.lunch_end = lunch_end
            
            db.session.add(work_period)
        
        db.session.commit()
        
        flash('Registro de ponto atualizado com sucesso!', 'success')
        return redirect(url_for('time_record.list_time_records'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar registro de ponto: {str(e)}', 'danger')
        return redirect(url_for('time_record.edit_time_record', id=id))

@time_record_bp.route('/time_records/<int:id>/delete', methods=['POST'])
def delete_time_record(id):
    work_day = WorkDay.query.get_or_404(id)
    
    try:
        db.session.delete(work_day)
        db.session.commit()
        
        flash('Registro de ponto excluído com sucesso!', 'success')
        return redirect(url_for('time_record.list_time_records'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir registro de ponto: {str(e)}', 'danger')
        return redirect(url_for('time_record.list_time_records'))
