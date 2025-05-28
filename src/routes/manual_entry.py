import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify

from src.models import db, Employee, WorkDay, WorkPeriod

manual_entry_bp = Blueprint('manual_entry', __name__, url_prefix='/manual-entry')

@manual_entry_bp.route('/')
def index():
    return render_template('manual_entry/index.html')

def validate_record(record_data):
    """Valida um registro de hora extra e retorna o resultado da validação"""
    record = {
        'employee_name': record_data.get('employee_name', '').strip(),
        'date': record_data.get('date', '').strip(),
        'start_time': record_data.get('start_time', '').strip(),
        'end_time': record_data.get('end_time', '').strip(),
        'status': 'valid',
        'message': '',
        'employee_id': None,
        'date_obj': None,
        'start_time_obj': None,
        'end_time_obj': None
    }
    
    # Validar funcionário
    if not record['employee_name']:
        record['status'] = 'error'
        record['message'] = 'Nome do funcionário não pode ser vazio'
        return record
    
    employee = Employee.query.filter_by(name=record['employee_name']).first()
    if not employee:
        record['status'] = 'error'
        record['message'] = f"Funcionário '{record['employee_name']}' não encontrado"
        return record
    
    record['employee_id'] = employee.id
    
    # Validar data
    if not record['date']:
        record['status'] = 'error'
        record['message'] = 'Data não pode ser vazia'
        return record
    
    try:
        # Tentar diferentes formatos de data
        formats = ['%d/%m/%y', '%d/%m/%Y', '%Y-%m-%d']
        date_parsed = False
        
        for fmt in formats:
            try:
                record['date_obj'] = datetime.strptime(record['date'], fmt).date()
                date_parsed = True
                break
            except ValueError:
                continue
        
        if not date_parsed:
            record['status'] = 'error'
            record['message'] = f"Formato de data inválido: {record['date']}. Use DD/MM/YY"
            return record
    except Exception as e:
        record['status'] = 'error'
        record['message'] = f"Erro ao processar data: {str(e)}"
        return record
    
    # Validar hora inicial
    if not record['start_time']:
        record['status'] = 'error'
        record['message'] = 'Hora Extra Inicial não pode ser vazia'
        return record
    
    try:
        record['start_time_obj'] = datetime.strptime(record['start_time'], '%H:%M').time()
    except Exception as e:
        record['status'] = 'error'
        record['message'] = f"Formato de hora inválido para Hora Extra Inicial: {str(e)}"
        return record
    
    # Validar hora final
    if not record['end_time']:
        record['status'] = 'error'
        record['message'] = 'Hora Extra Final não pode ser vazia'
        return record
    
    try:
        record['end_time_obj'] = datetime.strptime(record['end_time'], '%H:%M').time()
    except Exception as e:
        record['status'] = 'error'
        record['message'] = f"Formato de hora inválido para Hora Extra Final: {str(e)}"
        return record
    
    # Validar intervalo de tempo
    if record['start_time_obj'] > record['end_time_obj']:
        record['status'] = 'warning'
        record['message'] = 'Atenção: Hora final é anterior à hora inicial. Será considerado como período que cruza a meia-noite.'
    
    # Formatar para exibição
    record['date'] = record['date_obj'].strftime('%d/%m/%Y')
    record['start_time'] = record['start_time_obj'].strftime('%H:%M')
    record['end_time'] = record['end_time_obj'].strftime('%H:%M')
    
    return record

def save_record_to_database(record):
    """Salva um registro validado no banco de dados"""
    try:
        # Verificar se já existe um WorkDay para esta data e funcionário
        work_day = WorkDay.query.filter_by(
            employee_id=record['employee_id'],
            date=record['date_obj']
        ).first()
        
        # Se não existir, criar um novo
        if not work_day:
            work_day = WorkDay(
                employee_id=record['employee_id'],
                date=record['date_obj']
            )
            db.session.add(work_day)
            db.session.flush()  # Para obter o ID
        
        # Criar um novo período adicional
        work_period = WorkPeriod(
            work_day_id=work_day.id,
            period_type='additional',
            entry_time=record['start_time_obj'],
            exit_time=record['end_time_obj']
        )
        
        db.session.add(work_period)
        return True
    except Exception as e:
        db.session.rollback()
        print(f'Erro ao salvar registro: {str(e)}')
        return False

@manual_entry_bp.route('/process-single', methods=['POST'])
def process_single():
    """Processa um único registro inserido manualmente"""
    try:
        record_data = {
            'employee_name': request.form.get('employee_name', ''),
            'date': request.form.get('date', ''),
            'start_time': request.form.get('start_time', ''),
            'end_time': request.form.get('end_time', '')
        }
        
        record = validate_record(record_data)
        
        if record['status'] == 'error':
            flash(f"Erro: {record['message']}", 'danger')
            return render_template('manual_entry/index.html', error_message=record['message'])
        
        if save_record_to_database(record):
            db.session.commit()
            success_message = 'Registro de hora extra adicionado com sucesso!'
            flash(success_message, 'success')
            
            import_results = {
                'total_count': 1,
                'success_count': 1,
                'ignored_count': 0
            }
            
            return render_template('manual_entry/index.html', 
                                  success_message=success_message,
                                  import_results=import_results)
        else:
            return render_template('manual_entry/index.html', 
                                  error_message='Erro ao salvar o registro no banco de dados.')
    
    except Exception as e:
        db.session.rollback()
        error_message = f'Erro ao processar o registro: {str(e)}'
        flash(error_message, 'danger')
        return render_template('manual_entry/index.html', error_message=error_message)

@manual_entry_bp.route('/save-table-data', methods=['POST'])
def save_table_data():
    """Processa e salva os dados da tabela editável"""
    try:
        # Obter dados JSON do request
        data = request.get_json()
        
        if not data or 'records' not in data:
            return jsonify({
                'success': False,
                'message': 'Dados inválidos',
                'total_count': 0,
                'success_count': 0,
                'ignored_count': 0
            }), 400
        
        records = data['records']
        total_count = len(records)
        success_count = 0
        ignored_count = 0
        
        # Processar cada registro
        for record_data in records:
            # Pular linhas vazias
            if not record_data['employee_name'].strip() and not record_data['date'].strip() and \
               not record_data['start_time'].strip() and not record_data['end_time'].strip():
                continue
                
            # Validar o registro
            record = validate_record(record_data)
            
            # Salvar registros válidos ou com avisos
            if record['status'] == 'valid' or record['status'] == 'warning':
                if save_record_to_database(record):
                    success_count += 1
                else:
                    ignored_count += 1
            else:
                ignored_count += 1
        
        # Commit das alterações no banco
        db.session.commit()
        
        # Retornar resultados
        return jsonify({
            'success': True,
            'message': 'Registros processados com sucesso',
            'total_count': total_count,
            'success_count': success_count,
            'ignored_count': ignored_count
        })
    
    except Exception as e:
        db.session.rollback()
        print(f'Erro ao processar os registros: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'Erro ao processar os registros: {str(e)}',
            'total_count': 0,
            'success_count': 0,
            'ignored_count': 0
        }), 500
