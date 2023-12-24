from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectField, FloatField, \
    TextAreaField, FileField, IntegerField
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
                  ('West African CFA franc - XOF', 'West African CFA franc'),
                  ('Swiss Franc - CHF', 'Swiss Franc'), ('British Pound - GBP', 'British Pound'),
                  ('Canadian dollar - CAD', 'Canadian dollar'),
                  ('Japanese yen - JPY', 'Japanese yen')]
    account_cats = [('Chèque-repas', 'Chèque-repas'), ('Eco-chèques', 'Eco-chèques'),
                    ('Compte épargne', 'Compte épargne'), ('Compte courant', 'Compte courant')]
    category = SelectField('Category of expense account', choices=account_cats, validators=[DataRequired()])
    owner = StringField('Owner', validators=[DataRequired(), Length(min=2, max=50)])
    iban = StringField('IBAN', validators=[DataRequired()])
    bank = StringField('Bank', validators=[DataRequired(), Length(min=2, max=50)])
    balance = FloatField('Balance', validators=[Optional()])
    expiration_date = DateField('Expiration Date', validators=[DataRequired()])
    currency = SelectField('Currency', validators=[DataRequired()], choices=currencies)
    country = StringField('Country', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Submit')


class CreateIncomeForm(FlaskForm):
    categories = [('Reimbursments', 'Reimbursments'), ('Salaire', 'Salary'), ('Cadeaux', 'Gifts'),
                  ('Commission', 'Commission'),
                  ('Interest', 'Interest'), ('Investments', 'Investments'),
                  ('Government Payments', 'Government Payments')]
    account_id = SelectField('Account credited', validators=[DataRequired()])
    income_date = DateField('Income Date', validators=[DataRequired()])
    category = SelectField('Income Category ', choices=categories, validators=[DataRequired()])
    source = StringField('Source of the Income', validators=[DataRequired(), Length(min=2, max=50)])
    amount = FloatField('Income Amount', validators=[DataRequired()])
    submit = SubmitField('Submit')


class CreateDetailForm(FlaskForm):
    detail_quantity = FloatField('detail quantity',validators=[DataRequired()])
    detail_name = StringField('detail name', validators=[DataRequired(), Length(min=2, max=50)])
    detail_amount = FloatField('detail Amount', validators=[DataRequired()])
    submit = SubmitField('Submit')


class CreateExpenseForm(FlaskForm):
    categories = [('Mortgage or rent', 'Housing-Mortgage or rent'), ('Property taxes', 'Housing-Mortgage or rent'),
                  ('Household repairs', 'Housing-Household repairs'),('Car payment', 'Transportation-Car payment'),
                  ('Car warranty', 'Transportation-Car warranty'), ('Gas', 'Transportation-Gas'),
                  ('Tires', 'Transportation-Tires'), ('Repairs', 'Transportation-Repairs'),
                  ('Parking fees','Transportation-Parking fees'), ('Restaurants', 'Food-Restaurants'),
                  ('Groceries', 'Food-Groceries'), ('Internet', 'Utilities-Internet'),('Water', 'Utilities-Water'),
                  ('Garbage', 'Utilities-Garbage'), ('Phones', 'Utilities-Phones'),
                  ('Cable', 'Utilities-Cable'), ('Electricity', 'Utilities-Electricity'),
                  ('Alcohol/bars', 'Entertainment-Alcohol/bars'), ('Games', 'Entertainment-Games'),
                  ('Movies', 'Entertainment-Movies'), ('Concerts', 'Entertainment-Concerts'),
                  ('Vacations', 'Entertainment-Vacations'), ('Subscriptions', 'Entertainment-Subscriptions'),
                  ('Birthday', 'Gifts/Donations-Birthday'), ('Wedding', 'Gifts/Donations-Wedding'),
                  ('Christmas', 'Gifts/Donations-Christmas'),('Special occasion', 'Gifts/Donations-Special occasion'),
                  ('Charities', 'Gifts/Donations-Charities'),('Books', 'Education-Books'),
                  ('Emergency fund', 'Savings-Emergency fund'), ('Other savings', 'Savings-Other savings'),
                  ('Adults’ clothing', 'Clothing-Adults’ clothing'), ('Children’s clothing', 'Clothing-Children’s clothing'),
                  ('Primary care', 'Medical/Healthcare-Primary care'), ('Dental care', 'Medical/Healthcare-Dental care'),
                  ('Specialty care', 'Medical/Healthcare-Specialty care'), ('Gym memberships', 'Personal-Gym memberships'),
                  ('Haircuts', 'Personal-Haircuts'), ('Salon services', 'Personal-Salon services'), ('Cosmetics', 'Personal-Cosmetics'),
                  ('Investing', 'Retirement-Investing'), ('Financial planning', 'Retirement-Financial planning'),
                  ('Credit cards','Debt-Credit cards'), ('Other', 'Other')]

    account_id = SelectField('Account debited', validators=[DataRequired()])
    expense_date = DateField('Expense Date', validators=[DataRequired()])
    category = SelectField('Expense Category ', choices=categories, validators=[DataRequired()])
    proof = FileField('Expense Picture', validators=[FileAllowed(['jpg', 'png'])])
    merchant = StringField('Merchant', validators=[DataRequired(), Length(min=2, max=50)])
    description = TextAreaField('expense description')
    amount = FloatField('Expense Amount ', validators=[DataRequired()])
    submit = SubmitField('Submit')

