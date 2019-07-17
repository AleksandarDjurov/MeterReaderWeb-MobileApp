from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, Length, Email, EqualTo
from markupsafe import Markup

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                            validators=[DataRequired(), Length(min=2, max=20)])
    phone = StringField('Phone', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class ProfileForm(FlaskForm):
    username_profile = StringField('User Name',
                            validators=[DataRequired(), Length(min=2, max=20)])
    phone_profile = StringField('Phone', validators=[DataRequired()])
    password_profile = PasswordField('New Password', validators=None)
    confirm_password_profile = PasswordField('Confirm Password', validators=[EqualTo('password_profile')])

class LoginForm(FlaskForm):
    username = StringField('Username',
                            validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class CustomerAddForm(FlaskForm):
    firstname = StringField('First Name :',
                            validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last Name :', validators=[DataRequired()])
    mobile1 = IntegerField('Mobile Number 1 :', validators=[DataRequired()])
    mobile2 = IntegerField('Mobile Number 2 :', validators=None)
    mobile3 = IntegerField('Mobile Number 3 :', validators=None)
    mobile4 = IntegerField('Mobile Number 4 :', validators=None)
    district = SelectField('District :', validators=None, choices=[('GLA', 'GLA'), ('ARA', 'ARA'), ('FJA', 'FJA'), ('IFA', 'IFA'), ('MRA', 'MRA'), ('HSA', 'HSA')
                                                  , ('FNA', 'FNA'), ('CLA', 'CLA'), ('GWA', 'GWA'), ('SYA', 'SYA'), ('C2A', 'C2A'), ('UTA', 'UTA'), ('MKA', 'MKA')])
    city = SelectField('City :', validators=None, choices=[('Kismayo', 'Kismayo'), ('Baardheere', 'Baardheere')])
    neighbour = StringField('Neighbour :', validators=[DataRequired()])
    house_tax_no = StringField('House Tax Id No :', validators=[DataRequired()])
    customer_type = SelectField('Customer Type :', validators=None, choices=[('Domestic', 'Domestic'), ('Commercial', 'Commercial')])
    account_status = SelectField('Account Status :', validators=None, choices=[('On', 'On'), ('Off', 'Off')])
    dhameen_name = StringField('Dhameen Name :', validators=None)
    dhameen_mobile1 = IntegerField('Dhameen Mobile 1 :', validators=None)
    dhameen_mobile2 = IntegerField('Dhameen Mobile 2 :', validators=None)
    deposit = StringField('Deposit :', validators=None)
    comment = StringField('Comment :', validators=None)
    meter_make = SelectField('Meter Make :', validators=None, choices=[('WestHomes', 'WestHomes'), ('Sasun', 'Sasun')])
    meter_model = SelectField('Meter Model :', validators=None, choices=[('DD862', 'DD862'), ('DD862-4', 'DD862-4'), ('DTS999', 'DTS999')])
    meter_serial_no = StringField('Meter Serial No :', validators=[DataRequired()])
    tag_serial_no = StringField('Tag Serial No :', validators=[DataRequired()])
    curr_kw = StringField('Curr KW :', validators=None)
    # createdUser = SelectField('Customer Type :', validators=None, choices=[('Domestic', 'Domestic'), ('Commercial', 'Commercial')])
    created_user = StringField('Created By User :', validators=[DataRequired()])

class CustomerEditForm(FlaskForm):
    update_option = SelectField('Option :', validators=None, choices=[('oDetails', 'Update Customer Detail'), ('oTag', 'Tag Badal'), ('oSacad', 'Sacad Badal')])
    customer_id = IntegerField('Customer Id :')
    firstname = StringField('First Name :', validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last Name :', validators=[DataRequired()])
    mobile1 = IntegerField('Mobile Number 1 :', validators=[DataRequired()])
    mobile2 = IntegerField('Mobile Number 2 :', validators=None)
    mobile3 = IntegerField('Mobile Number 3 :', validators=None)
    mobile4 = IntegerField('Mobile Number 4 :', validators=None)
    district = StringField('District :', validators=[DataRequired()])
    city = SelectField('City :', validators=None, choices=[('Kismayo', 'Kismayo'), ('Baardheere', 'Baardheere')])
    neighbour = StringField('Neighbour :', validators=[DataRequired()])
    house_tax_no = StringField('House Tax Id No :', validators=[DataRequired()])
    customer_type = SelectField('Customer Type :', validators=None, choices=[('Domestic', 'Domestic'), ('Commercial', 'Commercial')])
    account_status = SelectField('Account Status :', validators=None, choices=[(1, 'On'), (0, 'Off')])
    dhameen_name = StringField('Dhameen Name :', validators=None)
    dhameen_mobile1 = IntegerField('Dhameen Mobile 1 :', validators=None)
    dhameen_mobile2 = IntegerField('Dhameen Mobile 2 :', validators=None)
    deposit = StringField('Deposit :', validators=None)
    comment = StringField('Comment :', validators=None)
    meter_make = SelectField('Meter Make :', validators=None, choices=[('WestHomes', 'WestHomes'), ('Sasun', 'Sasun')])
    meter_model = SelectField('Meter Model :', validators=None, choices=[('DD862', 'DD862'), ('DD862-4', 'DD862-4'), ('DTS999', 'DTS999')])
    meter_serial_no = StringField('Meter Serial No :', validators=None)
    tag_serial_no = StringField('Tag Serial No :', validators=None)
    meter_barcode_no = StringField('Meter Barcode No :', validators=[DataRequired()])
    meter_read = IntegerField('New Meter Read :', validators=None)
    user = StringField('Modified by :', validators=[DataRequired()])

class CustomerUsagesForm(FlaskForm):
    district = SelectField('District :', validators=None )
    months = SelectField('Month :', validators=None )

class CustomerForm(FlaskForm):
    district = SelectField('District :', validators=None )

class PaymentForm(FlaskForm):
    district = SelectField('District :', validators=None )
    months = SelectField('Month :', validators=None )

class ReportForm(FlaskForm):
    months_discounted = SelectField('Month :', validators=None )
    months_usage = SelectField('Month :', validators=None )
    isread = SelectField('Read :', validators=None )
class homeForm(FlaskForm):
    months = SelectField('Month :', validators=None )

class adminCustomerForm(FlaskForm):
    district = SelectField('District :', validators=None )
    district_update = SelectField('District :', validators=None )
