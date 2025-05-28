from datetime import datetime, time
import pandas as pd
from src.models import db, Employee, WorkDay, WorkPeriod

class ImportValidator:
    """Classe para validar e processar dados importados de planilha"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_employee(self, employee_name):
        """Valida se o funcionário existe no sistema"""
        if not employee_name or pd.isna(employee_name):
            return None, "Nome do funcionário não pode ser vazio"
        
        employee = Employee.query.filter_by(name=employee_name).first()
        if not employee:
            return None, f"Funcionário '{employee_name}' não encontrado no sistema"
        
        return employee, None
    
    def validate_date(self, date_value):
        """Valida e converte o valor de data"""
        if pd.isna(date_value):
            return None, "Data não pode ser vazia"
        
        try:
            # Se já for um objeto date, retorna diretamente
            if hasattr(date_value, 'date') and callable(getattr(date_value, 'date')):
                return date_value.date(), None
            
            # Se for um objeto datetime.date, retorna diretamente
            if hasattr(date_value, 'day') and hasattr(date_value, 'month') and hasattr(date_value, 'year'):
                return date_value, None
            
            # Se for string, tenta converter
            if isinstance(date_value, str):
                # Tenta diferentes formatos de data
                formats = ['%d/%m/%y', '%d/%m/%Y', '%Y-%m-%d']
                
                for fmt in formats:
                    try:
                        return datetime.strptime(date_value, fmt).date(), None
                    except ValueError:
                        continue
                
                return None, f"Formato de data inválido: {date_value}. Use DD/MM/YY"
            
            return None, f"Tipo de data não reconhecido: {type(date_value)}"
        
        except Exception as e:
            return None, f"Erro ao processar data: {str(e)}"
    
    def validate_time(self, time_value, field_name):
        """Valida e converte o valor de hora"""
        if pd.isna(time_value):
            return None, f"{field_name} não pode ser vazio"
        
        try:
            # Se já for um objeto time, retorna diretamente
            if isinstance(time_value, time):
                return time_value, None
            
            # Se for string, tenta converter
            if isinstance(time_value, str):
                return datetime.strptime(time_value, '%H:%M').time(), None
            
            # Se for um valor numérico (ex: Excel pode armazenar como fração do dia)
            if isinstance(time_value, (int, float)):
                # Converte de fração do dia para segundos
                seconds = int(time_value * 24 * 60 * 60)
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                
                # Garante que está dentro dos limites válidos
                if 0 <= hours < 24 and 0 <= minutes < 60:
                    return time(hours, minutes), None
            
            return None, f"Formato de hora inválido para {field_name}: {time_value}. Use HH:MM"
        
        except Exception as e:
            return None, f"Erro ao processar hora {field_name}: {str(e)}"
    
    def validate_time_range(self, start_time, end_time):
        """Valida se o intervalo de tempo é válido"""
        # Se ambos são do mesmo dia e o fim é antes do início
        if start_time > end_time:
            return "Atenção: Hora final é anterior à hora inicial. Será considerado como período que cruza a meia-noite."
        return None
    
    def process_record(self, record):
        """Processa e valida um registro da planilha"""
        result = {
            'employee_name': record.get('Nome Funcionário', ''),
            'date': record.get('Data', None),
            'start_time': record.get('Hora Extra Inicial', None),
            'end_time': record.get('Hora Extra Final', None),
            'status': 'valid',
            'message': '',
            'employee_id': None,
            'date_obj': None,
            'start_time_obj': None,
            'end_time_obj': None
        }
        
        # Validar funcionário
        employee, error = self.validate_employee(result['employee_name'])
        if error:
            result['status'] = 'error'
            result['message'] = error
            return result
        
        result['employee_id'] = employee.id
        
        # Validar data
        date_obj, error = self.validate_date(result['date'])
        if error:
            result['status'] = 'error'
            result['message'] = error
            return result
        
        result['date_obj'] = date_obj
        
        # Validar hora inicial
        start_time_obj, error = self.validate_time(result['start_time'], 'Hora Extra Inicial')
        if error:
            result['status'] = 'error'
            result['message'] = error
            return result
        
        result['start_time_obj'] = start_time_obj
        
        # Validar hora final
        end_time_obj, error = self.validate_time(result['end_time'], 'Hora Extra Final')
        if error:
            result['status'] = 'error'
            result['message'] = error
            return result
        
        result['end_time_obj'] = end_time_obj
        
        # Validar intervalo de tempo
        warning = self.validate_time_range(start_time_obj, end_time_obj)
        if warning:
            result['status'] = 'warning'
            result['message'] = warning
        
        # Formatar para exibição
        result['date'] = date_obj.strftime('%d/%m/%Y')
        result['start_time'] = start_time_obj.strftime('%H:%M')
        result['end_time'] = end_time_obj.strftime('%H:%M')
        
        return result
    
    def save_to_database(self, validated_records):
        """Salva os registros validados no banco de dados"""
        success_count = 0
        ignored_count = 0
        
        try:
            for record in validated_records:
                if record['status'] == 'valid' or record['status'] == 'warning':
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
                    success_count += 1
                else:
                    ignored_count += 1
            
            db.session.commit()
            return {
                'success': True,
                'success_count': success_count,
                'ignored_count': ignored_count,
                'message': f'Importação concluída com sucesso! {success_count} registros importados.'
            }
        
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'success_count': 0,
                'ignored_count': 0,
                'message': f'Erro ao salvar registros: {str(e)}'
            }
