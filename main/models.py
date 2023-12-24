from datetime import datetime

from flask_login import UserMixin

from main import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    expenses = db.relationship('Expense', backref='user')
    accounts = db.relationship('Account', backref='user')

    def __repr__(self):
        return f"User('{self.firstname}', '{self.lastname}', '{self.email}')"


class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    income_date = db.Column(db.DateTime, default=datetime.now())
    category = db.Column(db.String(50), nullable=False, default="Other")
    source = db.Column(db.String(50), nullable=False, default="Other")
    amount = db.Column(db.Float, nullable=False)


class ExpenseDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column('expense_id', db.Integer, db.ForeignKey('expense.id'))
    detail_id = db.Column('detail_id', db.Integer, db.ForeignKey('detail.id'))
    expense = db.relationship('Expense', back_populates='details', lazy=True)
    detail = db.relationship('Detail', back_populates='expenses', lazy=True)


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    owner = db.Column(db.String(50), nullable=False)
    iban = db.Column(db.String(37))
    bank = db.Column(db.String(50))
    balance = db.Column(db.Float, nullable=False)
    expiration_date = db.Column(db.DateTime, default=datetime.now())
    currency = db.Column(db.String(50), default="Euro")
    country = db.Column(db.String(50), nullable=False, default="Belgium")
    incomes = db.relationship('Income', backref='account', lazy=True)
    expenses = db.relationship('Expense', backref='account', lazy=True)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    expense_date = db.Column(db.DateTime, default=datetime.now())
    category = db.Column(db.String(50), nullable=False)
    proof = db.Column(db.String(50), default='default.jpg')
    merchant = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(50))
    amount = db.Column(db.Float, nullable=False)
    details = db.relationship('ExpenseDetail', back_populates='expense', lazy=True)


class Detail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    detail_name = db.Column(db.String(50), nullable=False)
    detail_quantity = db.Column(db.Integer, default=1)
    detail_amount = db.Column(db.Float, nullable=False)
    expenses = db.relationship('ExpenseDetail', back_populates='detail', lazy=True)
