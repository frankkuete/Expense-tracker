from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectField, FloatField, \
    DecimalField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional

from main.models import User


class RegistrationForm(FlaskForm):
    firstname = StringField('First name', validators=[DataRequired(), Length(min=2, max=50)])
    lastname = StringField('Last name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create account')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class CreateAccountForm(FlaskForm):
    currencies = [('Euro - EUR', 'Euro'), ('United States dollar - USD', 'United States dollar'),
     ('Central African CFA franc - XAF', 'Central African CFA franc'),
     ('West African CFA franc - XOF', 'West African CFA franc')]
    account_cats = [('Chèque-repas', 'Chèque-repas'), ('Eco-chèques', 'Eco-chèques'), ('Compte épargne', 'Compte épargne'), ('Compte courant', 'Compte courant')]
    category = SelectField('Category of expense account', choices=account_cats, validators=[DataRequired()])
    owner = StringField('Owner', validators=[DataRequired(), Length(min=2, max=50)])
    iban = StringField('IBAN', validators=[DataRequired()])
    bank = StringField('Bank', validators=[DataRequired(), Length(min=2, max=50)])
    balance = FloatField('Balance', validators=[Optional()])
    expiration_date = DateField('Expiration Date', validators=[DataRequired()])
    currency = SelectField('Currency', validators=[DataRequired()], choices= currencies)
    country = StringField('Country', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Submit')


categories = [ ('Reimbursments','Reimbursments'), ('Salaire', 'Salary'), ('Cadeaux','Gifts'), ('Commission', 'Commission'),
              ('Interest', 'Interest'),('Investments','Investments'), ('Government Payments','Government Payments')]


class CreateIncomeForm(FlaskForm):
    account_id = SelectField('Account credited', validators=[DataRequired()])
    income_date = DateField('Income Date', validators=[DataRequired()])
    category = SelectField('Income Category ', choices=categories, validators=[DataRequired()])
    source = StringField('Source of the Income', validators=[DataRequired(), Length(min=2, max=50)])
    amount = FloatField('Income Amount (in EURO)', validators=[DataRequired()])
    submit = SubmitField('Submit')
