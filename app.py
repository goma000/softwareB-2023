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
    categories = Menu.query.with_entities(Menu.category).distinct().all()
    return render_template('index.html', categories=categories)

@app.route('/menu_by_category/<category>')
def menu_by_category(category):
    menus = Menu.query.filter_by(category=category).all()
    return render_template('menu_card.html', menus=menus, category=category)



@app.route('/select_menu', methods=['POST'])
def select_menu():
    session['selected_menu'] = request.form['menu_id']
    return redirect(url_for('options'))

@app.route('/options')
def options():
    menu_id = session.get('selected_menu')
    selected_menu = Menu.query.get(menu_id) if menu_id else None
    return render_template('option.html', selected_menu=selected_menu)

@app.route('/select_options', methods=['POST'])
def select_options():
    session['pickup_location'] = request.form.get('pickup_location', 'default_pickup_location')
    session['coupon'] = request.form.get('coupon', 'no_coupon')
    session['payment_method'] = request.form.get('payment_method', 'default_payment')
    return redirect(url_for('order_confirmation'))

def calculate_total_price(menu_price, coupon, fee_rate=0.03):
    """注文の合計金額を計算する関数"""
    discount = 0
    if coupon == '5_percent_off':
        discount = int(menu_price * 0.05)  # 割引を切り捨て整数に
    elif coupon == '100_yen_off':
        discount = 100  # この割引は既に整数

    subtotal = max(int(menu_price - discount), 0)  # 割引後の小計を切り捨て整数に
    fee = int(subtotal * fee_rate)  # 手数料を切り捨て整数に
    total = subtotal + fee  # 合計金額を計算

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

    return render_template('confirmation.html', menu=menu, subtotal=subtotal, discount=discount, fee=fee, total=total, coupon=coupon, pickup_location=pickup_location, payment_method=payment_method)


@app.route('/finalize_order', methods=['POST'])
def finalize_order():
    # 注文の最終確定前に必要な情報を取得
    menu_id = session.get('selected_menu')
    menu = Menu.query.get(menu_id) if menu_id else None
    state_text = "配達中\nただいま商品を配達中です"
    # ...
    return render_template('finalize.html', menu=menu, state_text=state_text)

@app.route('/receipt')
def receipt():
    return render_template('receipt.html')

@app.route('/share')
def share():
    return render_template('share.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/add_menu', methods=['POST'])
def add_menu():
    # フォームからのデータを取得
    category = request.form.get('category')
    name = request.form.get('name')
    store = request.form.get('store')
    price = request.form.get('price')

    # 新しいメニューアイテムを作成してデータベースに追加
    if category and name and store and price:
        new_menu = Menu(category=category, name=name, store=store, price=price)
        db.session.add(new_menu)
        db.session.commit()
        return redirect(url_for('admin'))
    else:
        # データが不足している場合はエラーメッセージを表示
        return "必要なデータが不足しています", 400

@app.route('/delete_menu', methods=['POST'])
def delete_menu():
    # フォームからIDを取得
    menu_id = request.form.get('id')

    # 指定されたIDのメニューをデータベースから削除
    if menu_id:
        menu_to_delete = Menu.query.get(menu_id)
        if menu_to_delete:
            db.session.delete(menu_to_delete)
            db.session.commit()
            return redirect(url_for('admin'))
        else:
            return "指定されたIDのメニューが見つかりません", 404
    else:
        return "IDが指定されていません", 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

