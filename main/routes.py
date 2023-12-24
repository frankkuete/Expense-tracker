import os
import secrets
import time

from PIL import Image

from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, logout_user, login_user, login_required

from main import app, db, bcrypt
from main.forms import RegistrationForm, LoginForm, CreateAccountForm, CreateIncomeForm, CreateExpenseForm, \
    CreateDetailForm
from main.models import User, Account, Income, Expense, Detail, ExpenseDetail
from babel import numbers



@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title="Keep an eye on your expenses")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html', title="dashboard")


@app.route("/expenses")
@login_required
def expenses():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    for expense in expenses:
        related_account = Account.query.get(expense.account_id)
        expense.account_id = related_account.category+"-"+related_account.bank+"-"+related_account.iban
    return render_template('expenses.html', title="expenses", expenses=expenses)


@app.route("/expense/new", methods=['GET', 'POST'])
@login_required
def new_expense():
    form = CreateExpenseForm()
    form.account_id.choices = [(a.id, a.category + "-" + a.bank + "-" + a.iban) for a in Account.query.filter_by(user_id=current_user.id).all()]
    if form.validate_on_submit():
        expense = Expense(user_id=current_user.id, account_id=form.account_id.data, expense_date=form.expense_date.data, category=form.category.data,
                          merchant=form.merchant.data, description=form.description.data, amount=form.amount.data)
        if form.proof.data:
            expense.proof = save_picture(form.proof.data, 'expense_pics')
        account_to_update = Account.query.get_or_404(form.account_id.data)
        account_to_update.balance = account_to_update.balance - form.amount.data
        db.session.add(expense)
        db.session.commit()
        flash('Your new expense has been created ! ', 'success')
        return redirect(url_for('expenses'))
    return render_template('new_expense.html', title="new_expense", form=form)


@app.route("/expense/<int:expense_id>/update", methods=['GET', 'POST'])
@login_required
def update_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    form = CreateExpenseForm()
    form.account_id.choices = [(a.id, a.category + "-" + a.bank + "-" + a.iban) for a in Account.query.filter_by(user_id=current_user.id).all()]
    if form.validate_on_submit():
        expense.merchant = form.merchant.data
        expense.description = form.description.data
        expense.expense_date = form.expense_date.data
        expense.category = form.category.data
        if form.proof.data:
            print(form.proof.data)
            expense.proof = save_picture(form.proof.data, 'expense_pics')
        if expense.account_id == form.account_id.data:
            account = Account.query.get_or_404(form.account_id.data)
            account.balance = account.balance - (form.amount.data - expense.amount)

        else:
            old_account = Account.query.get_or_404(expense.account_id)
            new_account = Account.query.get_or_404(form.account_id.data)
            old_account.balance = old_account.balance + expense.amount
            new_account.balance = new_account.balance - form.amount.data
        expense.account_id = form.account_id.data
        expense.amount = form.amount.data
        print(form.proof.data)
        db.session.commit()
        flash('Your Expense has been updated!', 'success')
        return redirect(url_for('expenses'))
    elif request.method == 'GET':
        form.account_id.default = expense.account_id
        form.process()
        form.merchant.data = expense.merchant
        form.description.data = expense.description
        form.amount.data = expense.amount
        form.expense_date.data = expense.expense_date
        form.category.data = expense.category
    return render_template('new_expense.html', title='update_expense', form=form, legend='Update Expense')


@app.route("/expense/<int:expense_id>/delete", methods=['POST'])
@login_required
def delete_expense(expense_id):
    deleted_expense = Expense.query.get_or_404(expense_id)
    modified_account = Account.query.get_or_404(deleted_expense.account_id)
    modified_account.balance = modified_account.balance + deleted_expense.amount
    for detail in deleted_expense.details:
        db.session.delete(detail.detail)
        db.session.delete(detail)
    db.session.delete(deleted_expense)
    db.session.commit()
    flash('Your expense and the related details have been successfully deleted !', 'success')
    return redirect(url_for('expenses'))


@app.route("/expense/<int:expense_id>/new", methods=['GET', 'POST'])
@login_required
def new_expense_detail(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    form = CreateDetailForm()
    if form.validate_on_submit():
        new_detail = Detail(detail_name=form.detail_name.data, detail_quantity=form.detail_quantity.data,
                            detail_amount=form.detail_amount.data)
        db.session.add(new_detail)
        db.session.commit()
        new_expense_detail = ExpenseDetail(expense_id=expense.id, detail_id=new_detail.id)
        db.session.add(new_expense_detail)
        db.session.commit()
        flash('Your new detail has been created ! ', 'success')
        return redirect(url_for('expense', expense_id=expense.id))
    return render_template('new_expense_detail.html', title="new expense detail", expense=expense, form=form)


@app.route("/expense/<int:expense_id>/delete/<int:detail_id>", methods=['POST'])
@login_required
def delete_expense_detail(expense_id, detail_id):
    deleted_expense_detail = ExpenseDetail.query.filter_by(expense_id=expense_id,detail_id=detail_id).all()
    deleted_detail = Detail.query.get_or_404(detail_id)
    print("delete", deleted_expense_detail,deleted_detail)
    for ed in deleted_expense_detail:
        db.session.delete(ed)
    db.session.delete(deleted_detail)
    db.session.commit()
    flash('The Detail has been remove !', 'success')
    return redirect(url_for('expense', expense_id=expense_id))


@app.route("/expense/<int:expense_id>")
def expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    details = expense.details
    related_account = Account.query.get(expense.account_id)
    account_name = related_account.category + "-" + related_account.bank + "-" + related_account.iban
    currency = numbers.get_currency_symbol(related_account.currency.split("-")[1].strip(), locale='en')
    image_file = url_for('static', filename='expense_pics/' + expense.proof)
    return render_template('expense.html', title="single_expense", expense=expense, account_name=account_name, image_file=image_file,  currency=currency, details=details)


def save_picture(form_picture, folder):
    """This function takes picture-data as argument , save the image in the filesystem and then return the random
    name of the image """
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)  # transforms "monfichier.jpg" => "monfichier" , ".jpg"
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/'+str(folder), picture_fn)
    i = Image.open(form_picture)
    # output_size = (125, 125)
    #i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/incomes")
@login_required
def incomes():
    incomes = []
    for account in Account.query.filter_by(user_id=current_user.id).all():
        for income in account.incomes:
            incomes.append(income)
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
                              bank=form.bank.data, balance=balance, expiration_date=form.expiration_date.data,
                              currency=form.currency.data, country=form.country.data)
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
    deleted_incomes = Income.query.filter_by(account_id=account_id).all()
    db.session.delete(deleted_account)
    for income in deleted_incomes:
        db.session.delete(income)
    db.session.commit()
    print(deleted_account, deleted_incomes)
    flash('Your account and the related incomes have been successfully deleted !', 'success')
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



