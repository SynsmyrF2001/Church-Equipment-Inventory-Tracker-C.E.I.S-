from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, FloatField, validators
from wtforms.validators import DataRequired, Optional, Length
from datetime import date


class EquipmentForm(FlaskForm):
    """Form for adding/editing equipment"""
    name = StringField('Equipment Name', validators=[DataRequired(), Length(max=100)])
    category = SelectField('Category', choices=[
        ('audio', 'Audio Equipment'),
        ('video', 'Video Equipment'),
        ('lighting', 'Lighting Equipment'),
        ('instruments', 'Musical Instruments'),
        ('cables', 'Cables & Accessories'),
        ('computers', 'Computers & Electronics'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    model = StringField('Model', validators=[Optional(), Length(max=100)])
    serial_number = StringField('Serial Number', validators=[Optional(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    purchase_date = DateField('Purchase Date', validators=[Optional()])
    purchase_price = FloatField('Purchase Price', validators=[Optional()])


class CheckoutForm(FlaskForm):
    """Form for checking out equipment"""
    checked_out_by = StringField('Checked Out By', validators=[DataRequired(), Length(max=100)])
    expected_return_date = DateField('Expected Return Date', validators=[Optional()], default=date.today)
    notes = TextAreaField('Notes', validators=[Optional()])
    condition_out = SelectField('Condition', choices=[
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor')
    ], default='good', validators=[DataRequired()])


class CheckinForm(FlaskForm):
    """Form for checking in equipment"""
    checked_in_by = StringField('Checked In By', validators=[DataRequired(), Length(max=100)])
    notes = TextAreaField('Notes', validators=[Optional()])
    condition_in = SelectField('Condition', choices=[
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor')
    ], default='good', validators=[DataRequired()])


class SearchForm(FlaskForm):
    """Form for searching and filtering equipment"""
    search = StringField('Search Equipment')
    category = SelectField('Category', choices=[
        ('', 'All Categories'),
        ('audio', 'Audio Equipment'),
        ('video', 'Video Equipment'),
        ('lighting', 'Lighting Equipment'),
        ('instruments', 'Musical Instruments'),
        ('cables', 'Cables & Accessories'),
        ('computers', 'Computers & Electronics'),
        ('other', 'Other')
    ])
    status = SelectField('Status', choices=[
        ('', 'All Status'),
        ('available', 'Available'),
        ('in-use', 'In Use'),
        ('maintenance', 'Maintenance')
    ])
