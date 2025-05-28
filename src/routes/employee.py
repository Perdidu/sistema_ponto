from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from src.models import db, Employee

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/employees', methods=['GET'])
def list_employees():
    employees = Employee.query.all()
    return render_template('employees/index.html', employees=employees)

@employee_bp.route('/employees/new', methods=['GET'])
def new_employee():
    return render_template('employees/new.html')

@employee_bp.route('/employees', methods=['POST'])
def create_employee():
    try:
        name = request.form['name']
        salary = request.form['salary']
        workday_start = request.form['workday_start']
        workday_end = request.form['workday_end']
        lunch_duration = request.form['lunch_duration']
        
        employee = Employee(
            name=name,
            salary=salary,
            workday_start=workday_start,
            workday_end=workday_end,
            lunch_duration=lunch_duration
        )
        
        db.session.add(employee)
        db.session.commit()
        
        flash('Funcionário cadastrado com sucesso!', 'success')
        return redirect(url_for('employee.list_employees'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao cadastrar funcionário: {str(e)}', 'danger')
        return redirect(url_for('employee.new_employee'))

@employee_bp.route('/employees/<int:id>', methods=['GET'])
def show_employee(id):
    employee = Employee.query.get_or_404(id)
    return render_template('employees/show.html', employee=employee)

@employee_bp.route('/employees/<int:id>/edit', methods=['GET'])
def edit_employee(id):
    employee = Employee.query.get_or_404(id)
    return render_template('employees/edit.html', employee=employee)

@employee_bp.route('/employees/<int:id>', methods=['POST'])
def update_employee(id):
    employee = Employee.query.get_or_404(id)
    
    try:
        employee.name = request.form['name']
        employee.salary = request.form['salary']
        employee.workday_start = request.form['workday_start']
        employee.workday_end = request.form['workday_end']
        employee.lunch_duration = request.form['lunch_duration']
        
        db.session.commit()
        
        flash('Funcionário atualizado com sucesso!', 'success')
        return redirect(url_for('employee.list_employees'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar funcionário: {str(e)}', 'danger')
        return redirect(url_for('employee.edit_employee', id=id))

@employee_bp.route('/employees/<int:id>/delete', methods=['POST'])
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    
    try:
        db.session.delete(employee)
        db.session.commit()
        
        flash('Funcionário excluído com sucesso!', 'success')
        return redirect(url_for('employee.list_employees'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir funcionário: {str(e)}', 'danger')
        return redirect(url_for('employee.list_employees'))
