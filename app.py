from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your-database.db'
app.config['SECRET_KEY'] = 'your-secret-key'
db = SQLAlchemy(app)

class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    store = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)

@app.route('/')
def index():
    categories = Menu.query.distinct(Menu.category).all()
    return render_template('menu_selection.html', categories=categories)

@app.route('/menu/<category>')
def menu(category):
    menus = Menu.query.filter_by(category=category).all()
    return render_template('menu.html', menus=menus, category=category)

@app.route('/select_menu', methods=['POST'])
def select_menu():
    session['selected_menu'] = request.form['menu_id']
    return redirect(url_for('pickup_location'))

@app.route('/pickup_location')
def pickup_location():
    return render_template('pickup.html')

@app.route('/select_pickup', methods=['POST'])
def select_pickup():
    session['pickup_location'] = request.form['pickup_location']
    return redirect(url_for('coupon_selection'))

@app.route('/coupon_selection')
def coupon_selection():
    return render_template('coupon.html')

@app.route('/select_coupon', methods=['POST'])
def select_coupon():
    session['coupon'] = request.form['coupon']
    return redirect(url_for('payment_method'))

@app.route('/payment_method')
def payment_method():
    return render_template('payment.html')

@app.route('/select_payment', methods=['POST'])
def select_payment():
    session['payment_method'] = request.form['payment_method']
    return redirect(url_for('order_confirmation'))
def calculate_total_price(menu_price, coupon, fee_rate=0.03):
    """注文の合計金額を計算する関数"""
    discount = 0
    if coupon == '5_percent_off':
        discount = menu_price * 0.05
    elif coupon == '100_yen_off':
        discount = 100

    subtotal = max(menu_price - discount, 0)  # 割引後の小計
    fee = subtotal * fee_rate  # 手数料
    total = subtotal + fee  # 合計金額
    return subtotal, discount, fee, total

@app.route('/order_confirmation')
def order_confirmation():
    menu_id = session.get('selected_menu')
    menu = Menu.query.get(menu_id)
    coupon = session.get('coupon')
    pickup_location = session.get('pickup_location')
    payment_method = session.get('payment_method')

    if menu:
        subtotal, discount, fee, total = calculate_total_price(menu.price, coupon)
    else:
        subtotal, discount, fee, total = 0, 0, 0, 0

    return render_template('confirmation.html', menu=menu, subtotal=subtotal, discount=discount, fee=fee, total=total, pickup_location=pickup_location, payment_method=payment_method)


@app.route('/finalize_order', methods=['POST'])
def finalize_order():
    # 注文の最終確定前に必要な情報を取得
    menu_id = session.get('selected_menu')
    menu = Menu.query.get(menu_id) if menu_id else None
    # その他の注文情報を取得して確認画面に渡す
    # ...
    return render_template('finalize.html', menu=menu)

@app.route('/receipt')
def receipt():
    return render_template('receipt.html')

@app.route('/share')
def share():
    return render_template('share.html')

if __name__ == '__main__':
    app.run(debug=True)
