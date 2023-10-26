from flask import Flask, render_template, request, redirect, url_for
import json
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///company.db'  # Ustaw bazę danych SQLite
# current_inventory = []
# current_quantity_items = []
# current_price = []
# current_balance = 0
# history_data = []
purchases = []
sales_history = []
balance = float(0)

db = SQLAlchemy(app)


class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)


class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)


class BalanceChange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(10), nullable=False)
    value = db.Column(db.Float, nullable=False)
    new_balance = db.Column(db.Float, nullable=False)


@app.route('/', methods=['GET', 'POST'])
def purchase_form():
    if request.method == 'POST':
        product_name = request.form['product_name']
        unit_price = float(request.form['unit_price'])
        quantity = int(request.form['quantity'])
        total_cost = unit_price * quantity

        purchase = \
            {
                'product_name': product_name,
                'unit_price': unit_price,
                'quantity': quantity,
                'total_cost': total_cost
            }
        purchases.append(purchase)
        # history_data.append(purchase)
        # current_inventory.append(product_name)
        # current_quantity_items.append(quantity)
        # current_price.append(unit_price)

        with open('purchase_form.json', mode='a+') as file:
            file.write(json.dumps(purchase, indent=4))

        buy_transaction = Purchase(product_name=product_name, unit_price=unit_price, quantity=quantity,
                                   total_cost=total_cost)
        db.session.add(buy_transaction)
        db.session.commit()

        return render_template('home_page.html', product_name=product_name, unit_price=unit_price,
                               quantity=quantity, buy_transaction=buy_transaction)

    buy_transaction = Purchase.query.all()
    return render_template('home_page.html', purchases=purchases, buy_transaction=buy_transaction)


@app.route('/add_sale', methods=['GET', 'POST'])
def add_sale():
    if request.method == 'POST':
        product_name = request.form['product_name']
        unit_price = float(request.form['unit_price'])
        quantity = int(request.form['quantity'])
        total_price = unit_price * quantity

        sales = \
            {
                'product_name': product_name,
                'unit_price': unit_price,
                'quantity': quantity,
                'total_price': total_price
            }
        sales_history.append(sales)
        # purchases.remove(sales)

        with open('purchase_form.json', mode='a+') as file:
            file.write(json.dumps(sales, indent=4))

        sale_transaction = Sale(product_name=product_name, unit_price=unit_price, quantity=quantity)
        db.session.add(sale_transaction)
        db.session.commit()

        return render_template('add_sale.html', product_name=product_name, unit_price=unit_price,
                               quantity=quantity, sale_transactions=sale_transaction)

    sale_transactions = Sale.query.all()
    return render_template('add_sale.html', purchases=purchases, sales_history=sales_history,
                           sale_transactions=sale_transactions)


@app.route('/change_balance', methods=['GET', 'POST'])
def change_balance():
    global balance
    balance = float(0)

    if request.method == 'POST':
        comment = request.form.get('comment')
        value = request.form.get('value')
        try:
            if comment == 'add' or comment == 'Add':
                value = float(value)
                balance += value
                answer_add = f'Balance changed on plus by {value} in PLN.'

                added_balance = \
                    {
                        "Added": balance,
                        "Comment": answer_add
                    }

                with open('save_balance.json', mode='a+') as file:
                    file.write(json.dumps(added_balance, indent=4))

                balance_change_add = BalanceChange(comment=comment, value=value, new_balance=balance)
                db.session.add(balance_change_add)
                db.session.commit()

                return render_template('change_balance.html', answer_add=answer_add, balance=balance,
                                       balance_change_add=balance_change_add)

            elif comment == 'substract' or comment == 'Substract':
                value = float(value)
                balance -= value
                answer_substract = f'Balance changed on minus by {value} in PLN.'

                minus_balance = \
                    {
                        "Added": balance,
                        "Comment": answer_substract
                    }

                with open('save_balance.json', mode='a+') as file:
                    file.write(json.dumps(minus_balance, indent=4))

                balance_change_substract = BalanceChange(comment=comment, value=value,
                                                         new_balance=balance)
                db.session.add(balance_change_substract)
                db.session.commit()

                return render_template('change_balance.html', answer_substract=answer_substract, balance=balance,
                                       balance_change_substract=balance_change_substract)

        except ValueError:
            error = 'Error: Value must be a number.'

            error_json = \
                {
                    "Error": error
                }

            with open('save_balance.json', mode='a+') as file:
                file.write(json.dumps(error_json, indent=4))

            return render_template('change_balance.html', error=error)

        balance_change_add = BalanceChange.query.all()
        balance_change_substract = BalanceChange.query.all()
        return render_template('change_balance.html', comment=comment, balance=balance, value=value,
                               balance_change_add=balance_change_add, balance_change_substract=balance_change_substract)

    return render_template('change_balance.html', balance=balance)


@app.route('/history/')
@app.route('/history/<int:start>/')
@app.route('/history/<int:start>/<int:end>/')
def history(start=0, end=len(sales_history)):
    return render_template('history.html', purchases=purchases, sales_history=sales_history[start:end])


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
