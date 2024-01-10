from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your-database.db'
db = SQLAlchemy(app)

# モデルの定義
class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    store = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)

# メニュー選択画面
@app.route('/')
def menu():
    categories = Menu.query.distinct(Menu.category).all()
    return render_template('menu.html', categories=categories)

# カテゴリに基づくメニューの取得
@app.route('/category/<category_name>')
def category(category_name):
    menus = Menu.query.filter_by(category=category_name).all()
    return render_template('category.html', menus=menus, category=category_name)

# 以下のルートは、テンプレートファイルで提供されたフォームの処理に基づいている
@app.route('/pickup')
def pickup():
    return render_template('pickup.html')

@app.route('/coupon')
def coupon():
    return render_template('coupon.html')

@app.route('/payment')
def payment():
    return render_template('payment.html')

@app.route('/confirmation', methods=['POST'])
def confirmation():
    order_data = request.form
    return render_template('confirmation.html', order=order_data)

@app.route('/finalize')
def finalize():
    return render_template('finalize.html')

@app.route('/receipt')
def receipt():
    return render_template('receipt.html')

@app.route('/share')
def share():
    return render_template('share.html')

# 管理画面
@app.route('/admin')
def admin():
    return render_template('admin.html')

# メニュー追加処理
@app.route('/add_menu', methods=['POST'])
def add_menu():
    category = request.form['category']
    name = request.form['name']
    store = request.form['store']
    price = request.form['price']
    new_menu = Menu(category=category, name=name, store=store, price=price)
    db.session.add(new_menu)
    db.session.commit()
    return redirect(url_for('admin'))

# メニュー削除処理
@app.route('/delete_menu', methods=['POST'])
def delete_menu():
    menu_id = request.form['id']
    Menu.query.filter_by(id=menu_id).delete()
    db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
