from flask import render_template, redirect, url_for, flash, request, make_response, session, jsonify
from flask_babel import gettext, ngettext, lazy_gettext, get_locale
from app import app, db
from models import Equipment, CheckoutHistory, User, VerificationCode
from forms import EquipmentForm, CheckoutForm, CheckinForm, SearchForm
from auth_routes import auth_bp
from qr_utils import qr_generator, qr_scanner

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

@app.route('/checkout-form')
def checkout_form_page():
    """Quick checkout form page"""
    return render_template('checkout_form.html')

# QR Code Routes
@app.route('/equipment/<int:equipment_id>/qr')
def equipment_qr_code(equipment_id):
    """Generate and display QR code for equipment"""
    equipment = Equipment.query.get_or_404(equipment_id)
    
    # Generate QR code
    qr_base64 = qr_generator.generate_equipment_qr_base64(
        equipment.id, 
        equipment.name, 
        equipment.category
    )
    
    return render_template('equipment_qr.html', 
                         equipment=equipment, 
                         qr_code=qr_base64)

@app.route('/scan')
def scan_page():
    """QR code scanning page"""
    return render_template('scan_qr.html')

@app.route('/scan/<int:equipment_id>')
def scan_equipment(equipment_id):
    """Direct scan result for specific equipment"""
    equipment = Equipment.query.get_or_404(equipment_id)
    return render_template('scan_result.html', equipment=equipment)

@app.route('/api/scan', methods=['POST'])
def api_scan_qr():
    """API endpoint to process scanned QR code data"""
    try:
        data = request.get_json()
        qr_data = data.get('qr_data', '').strip()
        
        if not qr_data:
            return jsonify({'error': 'No QR data provided'}), 400
        
        # Parse QR code data
        parsed = qr_scanner.parse_qr_data(qr_data)
        
        if not parsed['success']:
            return jsonify({'error': parsed['error'], 'raw_data': parsed.get('raw_data')}), 400
        
        equipment_id = parsed['equipment_id']
        equipment = Equipment.query.get(equipment_id)
        
        if not equipment:
            return jsonify({'error': f'Equipment with ID {equipment_id} not found'}), 404
        
        # Return equipment information
        return jsonify({
            'success': True,
            'equipment': {
                'id': equipment.id,
                'name': equipment.name,
                'category': equipment.category,
                'status': equipment.status,
                'location': equipment.location,
                'model': equipment.model,
                'description': equipment.description
            },
            'scan_info': parsed
        })
        
    except Exception as e:
        logger.error(f"QR scan error: {str(e)}")
        return jsonify({'error': 'Failed to process QR code'}), 500

@app.route('/api/quick-checkout', methods=['POST'])
def api_quick_checkout():
    """Quick checkout via QR code scan"""
    try:
        data = request.get_json()
        equipment_id = data.get('equipment_id')
        checked_out_by = data.get('checked_out_by', '').strip()
        expected_return = data.get('expected_return_date')
        notes = data.get('notes', '').strip()
        
        if not equipment_id or not checked_out_by:
            return jsonify({'error': 'Equipment ID and checkout person are required'}), 400
        
        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            return jsonify({'error': 'Equipment not found'}), 404
        
        if equipment.status != 'available':
            return jsonify({'error': f'Equipment is currently {equipment.status}'}), 400
        
        # Parse expected return date
        expected_return_date = None
        if expected_return:
            try:
                expected_return_date = datetime.strptime(expected_return, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid return date format. Use YYYY-MM-DD'}), 400
        
        # Create checkout record
        checkout = CheckoutHistory(
            equipment_id=equipment.id,
            checked_out_by=checked_out_by,
            expected_return_date=expected_return_date,
            notes=notes,
            condition_out='good'  # Default condition
        )
        
        # Update equipment status
        equipment.status = 'in-use'
        
        db.session.add(checkout)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Equipment "{equipment.name}" checked out successfully',
            'checkout': {
                'id': checkout.id,
                'equipment_name': equipment.name,
                'checked_out_by': checkout.checked_out_by,
                'checked_out_at': checkout.checked_out_at.isoformat(),
                'expected_return_date': checkout.expected_return_date.isoformat() if checkout.expected_return_date else None
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Quick checkout error: {str(e)}")
        return jsonify({'error': 'Failed to checkout equipment'}), 500

@app.route('/api/quick-checkin', methods=['POST'])
def api_quick_checkin():
    """Quick checkin via QR code scan"""
    try:
        data = request.get_json()
        equipment_id = data.get('equipment_id')
        checked_in_by = data.get('checked_in_by', '').strip()
        condition = data.get('condition', 'good')
        notes = data.get('notes', '').strip()
        
        if not equipment_id or not checked_in_by:
            return jsonify({'error': 'Equipment ID and checkin person are required'}), 400
        
        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            return jsonify({'error': 'Equipment not found'}), 404
        
        if equipment.status != 'in-use':
            return jsonify({'error': f'Equipment is not currently checked out (status: {equipment.status})'}), 400
        
        # Find active checkout
        active_checkout = CheckoutHistory.query.filter_by(
            equipment_id=equipment.id,
            checked_in_at=None
        ).first()
        
        if not active_checkout:
            return jsonify({'error': 'No active checkout found for this equipment'}), 400
        
        # Update checkout record
        active_checkout.checked_in_at = datetime.utcnow()
        active_checkout.checked_in_by = checked_in_by
        active_checkout.condition_in = condition
        if notes:
            active_checkout.notes = (active_checkout.notes or '') + f'\nCheck-in notes: {notes}'
        
        # Update equipment status based on condition
        if condition == 'poor':
            equipment.status = 'maintenance'
        else:
            equipment.status = 'available'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Equipment "{equipment.name}" checked in successfully',
            'checkin': {
                'id': active_checkout.id,
                'equipment_name': equipment.name,
                'checked_in_by': active_checkout.checked_in_by,
                'checked_in_at': active_checkout.checked_in_at.isoformat(),
                'condition': condition,
                'duration_days': active_checkout.duration_days
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Quick checkin error: {str(e)}")
        return jsonify({'error': 'Failed to checkin equipment'}), 500

@app.route('/api/equipment/list')
def api_equipment_list():
    """API endpoint to get list of all equipment for forms"""
    try:
        equipment = Equipment.query.all()
        equipment_list = []
        
        for eq in equipment:
            equipment_list.append({
                'id': eq.id,
                'name': eq.name,
                'category': eq.category,
                'status': eq.status,
                'location': eq.location,
                'model': eq.model,
                'description': eq.description
            })
        
        return jsonify(equipment_list)
        
    except Exception as e:
        logger.error(f"Equipment list error: {str(e)}")
        return jsonify({'error': 'Failed to load equipment list'}), 500
from datetime import datetime, date
import csv
import logging

logger = logging.getLogger(__name__)
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
