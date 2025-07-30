from flask import render_template, redirect, url_for, flash, request, make_response, session, jsonify
from flask_babel import gettext, ngettext, lazy_gettext, get_locale
from app import app, db
from models import Equipment, CheckoutHistory, User, VerificationCode
from forms import EquipmentForm, CheckoutForm, CheckinForm, SearchForm
from auth_routes import auth_bp

# Register authentication blueprint
app.register_blueprint(auth_bp)

# JWT Authentication Demo Routes
@app.route('/auth-demo')
def auth_demo():
    """Demo page showing authentication features"""
    return render_template('auth_demo.html')

@app.route('/protected-demo')
def protected_demo():
    """Demo protected page requiring authentication"""
    return render_template('protected_demo.html')
from datetime import datetime, date
import csv
from io import StringIO


@app.route('/')
def index():
    """Dashboard showing equipment overview"""
    search_form = SearchForm()
    
    # Get search parameters
    search_query = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    status_filter = request.args.get('status', '')
    
    # Build query
    query = Equipment.query
    
    if search_query:
        query = query.filter(Equipment.name.contains(search_query))
    
    if category_filter:
        query = query.filter(Equipment.category == category_filter)
    
    if status_filter:
        query = query.filter(Equipment.status == status_filter)
    
    equipment_list = query.order_by(Equipment.name).all()
    
    # Get statistics
    total_equipment = Equipment.query.count()
    available_count = Equipment.query.filter_by(status='available').count()
    in_use_count = Equipment.query.filter_by(status='in-use').count()
    maintenance_count = Equipment.query.filter_by(status='maintenance').count()
    
    # Get recent activity
    recent_activity = CheckoutHistory.query.order_by(CheckoutHistory.checked_out_at.desc()).limit(5).all()
    
    # Get overdue items
    overdue_items = []
    active_checkouts = CheckoutHistory.query.filter_by(checked_in_at=None).all()
    for checkout in active_checkouts:
        if checkout.is_overdue:
            overdue_items.append(checkout)
    
    return render_template('index.html', 
                         equipment_list=equipment_list,
                         search_form=search_form,
                         search_query=search_query,
                         category_filter=category_filter,
                         status_filter=status_filter,
                         total_equipment=total_equipment,
                         available_count=available_count,
                         in_use_count=in_use_count,
                         maintenance_count=maintenance_count,
                         recent_activity=recent_activity,
                         overdue_items=overdue_items)


@app.route('/equipment/add', methods=['GET', 'POST'])
def add_equipment():
    """Add new equipment"""
    form = EquipmentForm()
    
    if form.validate_on_submit():
        equipment = Equipment(
            name=form.name.data,
            category=form.category.data,
            model=form.model.data,
            serial_number=form.serial_number.data,
            description=form.description.data,
            location=form.location.data,
            purchase_date=form.purchase_date.data,
            purchase_price=form.purchase_price.data
        )
        
        db.session.add(equipment)
        db.session.commit()
        
        flash(f'Equipment "{equipment.name}" has been added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('equipment_form.html', form=form, title='Add Equipment')


@app.route('/equipment/<int:id>')
def equipment_detail(id):
    """View equipment details and history"""
    equipment = Equipment.query.get_or_404(id)
    history = CheckoutHistory.query.filter_by(equipment_id=id).order_by(CheckoutHistory.checked_out_at.desc()).all()
    
    return render_template('equipment_detail.html', equipment=equipment, history=history)


@app.route('/equipment/<int:id>/edit', methods=['GET', 'POST'])
def edit_equipment(id):
    """Edit equipment details"""
    equipment = Equipment.query.get_or_404(id)
    form = EquipmentForm(obj=equipment)
    
    if form.validate_on_submit():
        form.populate_obj(equipment)
        equipment.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash(f'Equipment "{equipment.name}" has been updated successfully!', 'success')
        return redirect(url_for('equipment_detail', id=equipment.id))
    
    return render_template('equipment_form.html', form=form, title='Edit Equipment', equipment=equipment)


@app.route('/equipment/<int:id>/delete', methods=['POST'])
def delete_equipment(id):
    """Delete equipment"""
    equipment = Equipment.query.get_or_404(id)
    
    # Check if equipment is currently checked out
    if equipment.status == 'in-use':
        flash('Cannot delete equipment that is currently checked out!', 'error')
        return redirect(url_for('equipment_detail', id=id))
    
    db.session.delete(equipment)
    db.session.commit()
    
    flash(f'Equipment "{equipment.name}" has been deleted successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/equipment/<int:id>/checkout', methods=['GET', 'POST'])
def checkout_equipment(id):
    """Check out equipment"""
    equipment = Equipment.query.get_or_404(id)
    
    if equipment.status != 'available':
        flash('Equipment is not available for checkout!', 'error')
        return redirect(url_for('equipment_detail', id=id))
    
    form = CheckoutForm()
    
    if form.validate_on_submit():
        checkout = CheckoutHistory(
            equipment_id=equipment.id,
            checked_out_by=form.checked_out_by.data,
            expected_return_date=form.expected_return_date.data,
            notes=form.notes.data,
            condition_out=form.condition_out.data
        )
        
        equipment.status = 'in-use'
        
        db.session.add(checkout)
        db.session.commit()
        
        flash(f'Equipment "{equipment.name}" has been checked out to {checkout.checked_out_by}!', 'success')
        return redirect(url_for('equipment_detail', id=equipment.id))
    
    return render_template('checkout_form.html', form=form, equipment=equipment, action='checkout')


@app.route('/equipment/<int:id>/checkin', methods=['GET', 'POST'])
def checkin_equipment(id):
    """Check in equipment"""
    equipment = Equipment.query.get_or_404(id)
    
    if equipment.status != 'in-use':
        flash('Equipment is not currently checked out!', 'error')
        return redirect(url_for('equipment_detail', id=id))
    
    current_checkout = equipment.current_checkout
    if not current_checkout:
        flash('No active checkout found for this equipment!', 'error')
        return redirect(url_for('equipment_detail', id=id))
    
    form = CheckinForm()
    
    if form.validate_on_submit():
        current_checkout.checked_in_at = datetime.utcnow()
        current_checkout.checked_in_by = form.checked_in_by.data
        current_checkout.notes = form.notes.data
        current_checkout.condition_in = form.condition_in.data
        
        # Update equipment status based on condition
        if form.condition_in.data == 'poor':
            equipment.status = 'maintenance'
        else:
            equipment.status = 'available'
        
        db.session.commit()
        
        flash(f'Equipment "{equipment.name}" has been checked in successfully!', 'success')
        return redirect(url_for('equipment_detail', id=equipment.id))
    
    return render_template('checkout_form.html', form=form, equipment=equipment, 
                         current_checkout=current_checkout, action='checkin')


@app.route('/equipment/<int:id>/maintenance')
def toggle_maintenance(id):
    """Toggle equipment maintenance status"""
    equipment = Equipment.query.get_or_404(id)
    
    if equipment.status == 'in-use':
        flash('Cannot change status of equipment that is currently checked out!', 'error')
        return redirect(url_for('equipment_detail', id=id))
    
    if equipment.status == 'maintenance':
        equipment.status = 'available'
        flash(f'Equipment "{equipment.name}" is now available!', 'success')
    else:
        equipment.status = 'maintenance'
        flash(f'Equipment "{equipment.name}" is now in maintenance!', 'warning')
    
    db.session.commit()
    return redirect(url_for('equipment_detail', id=id))


@app.route('/reports')
def reports():
    """Equipment usage reports"""
    # Get equipment usage statistics
    equipment_stats = []
    for equipment in Equipment.query.all():
        total_checkouts = CheckoutHistory.query.filter_by(equipment_id=equipment.id).count()
        active_checkout = equipment.current_checkout
        
        # Calculate total usage days
        completed_checkouts = CheckoutHistory.query.filter(
            CheckoutHistory.equipment_id == equipment.id,
            CheckoutHistory.checked_in_at.isnot(None)
        ).all()
        
        total_usage_days = sum([checkout.duration_days for checkout in completed_checkouts])
        
        equipment_stats.append({
            'equipment': equipment,
            'total_checkouts': total_checkouts,
            'total_usage_days': total_usage_days,
            'active_checkout': active_checkout
        })
    
    # Sort by most used
    equipment_stats.sort(key=lambda x: x['total_checkouts'], reverse=True)
    
    # Get monthly checkout statistics
    monthly_stats = {}
    all_checkouts = CheckoutHistory.query.all()
    for checkout in all_checkouts:
        month_key = checkout.checked_out_at.strftime('%Y-%m')
        if month_key not in monthly_stats:
            monthly_stats[month_key] = 0
        monthly_stats[month_key] += 1
    
    return render_template('reports.html', 
                         equipment_stats=equipment_stats,
                         monthly_stats=monthly_stats)


@app.route('/export/equipment')
def export_equipment():
    """Export equipment list to CSV"""
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Name', 'Category', 'Model', 'Serial Number', 'Status', 'Location', 'Purchase Date', 'Purchase Price'])
    
    # Write equipment data
    for equipment in Equipment.query.all():
        writer.writerow([
            equipment.name,
            equipment.category,
            equipment.model or '',
            equipment.serial_number or '',
            equipment.status,
            equipment.location or '',
            equipment.purchase_date.strftime('%Y-%m-%d') if equipment.purchase_date else '',
            equipment.purchase_price or ''
        ])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=equipment_inventory.csv'
    
    return response


@app.route('/export/history')
def export_history():
    """Export checkout history to CSV"""
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Equipment', 'Checked Out By', 'Checked Out At', 'Expected Return', 'Checked In At', 'Checked In By', 'Duration Days', 'Condition Out', 'Condition In', 'Notes'])
    
    # Write history data
    for history in CheckoutHistory.query.join(Equipment).order_by(CheckoutHistory.checked_out_at.desc()).all():
        writer.writerow([
            history.equipment.name,
            history.checked_out_by,
            history.checked_out_at.strftime('%Y-%m-%d %H:%M'),
            history.expected_return_date.strftime('%Y-%m-%d') if history.expected_return_date else '',
            history.checked_in_at.strftime('%Y-%m-%d %H:%M') if history.checked_in_at else 'Still Out',
            history.checked_in_by or '',
            history.duration_days,
            history.condition_out,
            history.condition_in or '',
            history.notes or ''
        ])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=checkout_history.csv'
    
    return response


@app.route('/set_language/<language>')
def set_language(language):
    """Set the user's preferred language"""
    if language in app.config['LANGUAGES']:
        session['language'] = language
        flash(f'Language changed to {app.config["LANGUAGES"][language]}', 'success')
    return redirect(request.referrer or url_for('index'))


@app.route('/tutorial')
def tutorial():
    """Show interactive tutorial for new users"""
    return render_template('tutorial.html')


@app.route('/tutorial/complete', methods=['POST'])
def complete_tutorial():
    """Mark tutorial as completed for user"""
    session['tutorial_completed'] = True
    flash('Tutorial completed! You\'re ready to start managing equipment.', 'success')
    return jsonify({'success': True, 'redirect': url_for('index')})
