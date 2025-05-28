from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
from src.models import db, Holiday

holiday_bp = Blueprint('holiday', __name__)

@holiday_bp.route('/holidays', methods=['GET'])
def list_holidays():
    year = request.args.get('year', type=int, default=datetime.now().year)
    holidays = Holiday.query.filter(db.extract('year', Holiday.date) == year).order_by(Holiday.date).all()
    return render_template('holidays/index.html', holidays=holidays, year=year)

@holiday_bp.route('/holidays/new', methods=['GET'])
def new_holiday():
    return render_template('holidays/new.html')

@holiday_bp.route('/holidays', methods=['POST'])
def create_holiday():
    try:
        holiday_date = request.form['date']
        description = request.form['description']
        
        # Verificar se já existe feriado nesta data
        existing_holiday = Holiday.query.filter_by(date=holiday_date).first()
        
        if existing_holiday:
            flash('Já existe um feriado cadastrado nesta data.', 'danger')
            return redirect(url_for('holiday.edit_holiday', id=existing_holiday.id))
        
        holiday = Holiday(
            date=holiday_date,
            description=description
        )
        
        db.session.add(holiday)
        db.session.commit()
        
        flash('Feriado cadastrado com sucesso!', 'success')
        return redirect(url_for('holiday.list_holidays'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao cadastrar feriado: {str(e)}', 'danger')
        return redirect(url_for('holiday.new_holiday'))

@holiday_bp.route('/holidays/<int:id>/edit', methods=['GET'])
def edit_holiday(id):
    holiday = Holiday.query.get_or_404(id)
    return render_template('holidays/edit.html', holiday=holiday)

@holiday_bp.route('/holidays/<int:id>', methods=['POST'])
def update_holiday(id):
    holiday = Holiday.query.get_or_404(id)
    
    try:
        holiday.date = request.form['date']
        holiday.description = request.form['description']
        
        db.session.commit()
        
        flash('Feriado atualizado com sucesso!', 'success')
        return redirect(url_for('holiday.list_holidays'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar feriado: {str(e)}', 'danger')
        return redirect(url_for('holiday.edit_holiday', id=id))

@holiday_bp.route('/holidays/<int:id>/delete', methods=['POST'])
def delete_holiday(id):
    holiday = Holiday.query.get_or_404(id)
    
    try:
        db.session.delete(holiday)
        db.session.commit()
        
        flash('Feriado excluído com sucesso!', 'success')
        return redirect(url_for('holiday.list_holidays'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir feriado: {str(e)}', 'danger')
        return redirect(url_for('holiday.list_holidays'))
