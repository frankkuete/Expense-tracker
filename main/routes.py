from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, logout_user, login_user, login_required

from main import app, db, bcrypt
from main.forms import RegistrationForm, LoginForm, CreateAccountForm, CreateIncomeForm
from main.models import User, Account, Income
from babel import numbers

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title="Keep an eye on your expenses")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html', title="dashboard")


@app.route("/incomes")
@login_required
def incomes():
    # TO-DO : get only the incomes related to the accounts of the current_user.user_id
    incomes = Income.query.all()
    for income in incomes:
        related_account = Account.query.get(income.account_id)
        income.account_id = related_account.category+"-"+related_account.bank+"-"+related_account.iban
    return render_template('incomes.html', title="incomes", incomes=incomes)


@app.route("/income/new", methods=['GET', 'POST'])
@login_required
def new_income():
    form = CreateIncomeForm()
    form.account_id.choices = [(a.id, a.category+"-"+a.bank+"-"+a.iban) for a in Account.query.filter_by(user_id = current_user.id).all()]
    if form.validate_on_submit():
        new_income = Income(account_id=form.account_id.data, category=form.category.data,
                            income_date=form.income_date.data, amount=form.amount.data,
                            source=form.source.data)
        account = Account.query.get_or_404(form.account_id.data)
        account.balance = account.balance + form.amount.data
        db.session.add(new_income)
        db.session.commit()
        flash('Your new income has been created ! ', 'success')
        return redirect(url_for('incomes'))
    return render_template('new_income.html', title="new_income", form=form)


@app.route("/income/<int:income_id>/update", methods=['GET', 'POST'])
@login_required
def update_income(income_id):
    income = Income.query.get_or_404(income_id)
    form = CreateIncomeForm()
    form.account_id.choices = [(a.id, a.category + "-" + a.bank + "-" + a.iban) for a in Account.query.filter_by(user_id=current_user.id).all()]
    if form.validate_on_submit():
        income.category = form.category.data
        income.income_date = form.income_date.data
        income.source = form.source.data
        if income.account_id == form.account_id.data:
            account = Account.query.get_or_404(form.account_id.data)
            account.balance = account.balance + (form.amount.data - income.amount)
        else:
            old_account = Account.query.get_or_404(income.account_id)
            new_account = Account.query.get_or_404(form.account_id.data)
            old_account.balance = old_account.balance - income.amount
            new_account.balance = new_account.balance + form.amount.data
        income.account_id = form.account_id.data
        income.amount = form.amount.data
        db.session.commit()
        flash('Your Income has been updated!', 'success')
        #return redirect(url_for('account', account_id=account.id))
        return redirect(url_for('incomes'))
    elif request.method == 'GET':
        account = Account.query.filter_by(user_id=current_user.id, id=income.account_id).first()
        form.account_id.default = account.id
        form.process()
        form.category.data = income.category
        form.income_date.data = income.income_date
        form.amount.data = income.amount
        form.source.data = income.source
        print("form account_id = ", form.account_id.data)
        print("form category = ", form.category.data)
    return render_template('new_income.html', title='update_income', form=form, legend='Update Income')


@app.route("/income/<int:income_id>/delete", methods=['POST'])
@login_required
def delete_income(income_id):
    deleted_income = Income.query.get_or_404(income_id)
    account = Account.query.get_or_404(deleted_income.account_id)
    account.balance = account.balance - deleted_income.amount
    db.session.delete(deleted_income)
    db.session.commit()
    flash('Your income has been successfully deleted !', 'success')
    return redirect(url_for('incomes'))

@app.route("/accounts")
@login_required
def accounts():
    # TO-DO : get only the accounts for the current_user.user_id
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    for account in accounts:
        account.currency = numbers.get_currency_symbol(account.currency.split("-")[1].strip(), locale='en')
    return render_template('accounts.html', title="accounts", accounts=accounts)


@app.route("/account/new", methods=['GET', 'POST'])
@login_required
def new_account():
    form = CreateAccountForm()
    #print("is validate:",form.validate())
    #print("is submit :",form.is_submitted())
    #print("validate errors:", form.errors)
    if form.validate_on_submit():
        balance = 0.0
        if form.balance.data is None:
            balance = form.balance.data
        new_account = Account(user_id =current_user.id, category=form.category.data, owner=form.owner.data, iban=form.iban.data,
                              bank=form.bank.data,balance=balance, expiration_date=form.expiration_date.data,
                              currency=form.currency.data,country=form.country.data)
        db.session.add(new_account)
        db.session.commit()
        flash('Your new expense account has been created ! ', 'success')
        return redirect(url_for('accounts'))
    return render_template('new_account.html', title="new_account", form=form)


@app.route("/account/<int:account_id>")
def account(account_id):
    account = Account.query.get_or_404(account_id)
    account.currency = numbers.get_currency_symbol(account.currency.split("-")[1].strip(), locale='en')
    return render_template('account.html', title="single_account", account=account)


@app.route("/account/<int:account_id>/delete", methods=['POST'])
@login_required
def delete_account(account_id):
    deleted_account = Account.query.get_or_404(account_id)
    db.session.delete(deleted_account)
    db.session.commit()
    flash('Your account has been successfully deleted !', 'success')
    return redirect(url_for('accounts'))


@app.route("/account/<int:account_id>/update", methods=['GET', 'POST'])
@login_required
def update_account(account_id):
    account = Account.query.get_or_404(account_id)
    form = CreateAccountForm()
    if form.validate_on_submit():
        account.category = form.category.data
        account.owner = form.owner.data
        account.bank = form.bank.data
        account.expiration_date = form.expiration_date.data
        account.iban = form.iban.data
        account.currency = form.currency.data
        account.country = form.country.data
        db.session.commit()
        flash('Your Expense account has been updated!', 'success')
        #return redirect(url_for('account', account_id=account.id))
        return redirect(url_for('accounts'))
    elif request.method == 'GET':
        form.category.data = account.category
        form.owner.data = account.owner
        form.bank.data = account.bank
        form.expiration_date.data = account.expiration_date
        form.iban.data = account.iban
        form.currency.data = account.currency
        form.country.data = account.country
    return render_template('new_account.html', title='update_account', form=form, legend='Update Account')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(firstname=form.firstname.data, lastname=form.lastname.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # if a user try to avoid required login, he will be redirected here
            # next_page is the view that the user try to access without required login
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful, Please check email and password', 'error')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


