from flask import Flask, render_template, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
import sys

# Flask App Oluşturma
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///watches.db"
app.config["SECRET_KEY"] = "QWEQWEQWE"
db = SQLAlchemy(app)


# Veritabanlanı Oluşturma 
class Watches(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String, nullable=False)
    model = db.Column(db.String, unique=True, nullable=False)
    image_url = db.Column(db.String, nullable=False)
    features = db.Column(db.Text)
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    order_items = db.Column(db.Integer, nullable=False, unique=True)
    order_quanity = db.Column(db.Integer, nullable=False)


class Orders_Detail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer)
    total = db.Column(db.Integer, nullable=False)
    created_time = db.Column(db.Text, nullable=False)



class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
       

with app.app_context():
    db.create_all()


#######################
# Site Yönlendirmeleri

@app.route('/')
def index():
    watches = db.session.execute(db.select(Watches)).scalars()

    distinct_brands = db.session.query(Watches.brand.distinct()).order_by(Watches.brand).all()
    new_distinct_brands = []
    for brand in distinct_brands: new_distinct_brands.append(brand[0])

    return render_template('index.html', watches= watches, brands = new_distinct_brands)


@app.route('/account')
def account_html():
    return render_template('account.html')

@app.route('/basket')
def basket_html():
    basket = db.session.execute(db.select(Orders)).scalars()
    watches = db.session.execute(db.select(Watches)).scalars()

    return render_template('basket.html', basket= basket, watches= watches)

@app.route('/admin')
def admin_html():
    watches = db.session.execute(db.select(Watches)).scalars()

    return render_template('admin.html', watches= watches)

@app.route('/about')
def about_html():
    return render_template('about.html')

########################
# Sitede Arama İşlemleri 

@app.route('/search', methods=['POST'])
def search_html():
    search_item = request.form.get('searchPlace')

    query = Watches.query.filter((Watches.brand.like(f'%{search_item}%')) |
                                 (Watches.model.like(f'%{search_item}%')) |
                                 (Watches.features.like(f'%{search_item}%'))).all()
    #print(query, file=sys.stderr)

    distinct_brands = db.session.query(Watches.brand.distinct()).order_by(Watches.brand).all()
    new_distinct_brands = []
    for brand in distinct_brands: new_distinct_brands.append(brand[0])

    return render_template('search.html', watches = query, search_item = search_item, search_len = len(query), brands = new_distinct_brands)


@app.route('/brand/<brand>')
def brand_search(brand):
    watches = db.session.execute(db.select(Watches).filter_by(brand=brand)).scalars()

    distinct_brands = db.session.query(Watches.brand.distinct()).order_by(Watches.brand).all()
    new_distinct_brands = []
    for d_brand in distinct_brands: new_distinct_brands.append(d_brand[0])


    return render_template('brand.html', watches=watches, brands = new_distinct_brands, brand = brand)


##################
# Admin İşlemleri

@app.route('/addWatch', methods=['POST'])
def add_item():
    brand = request.form.get('inputBrand')
    model  = request.form.get('inputModel')
    image_url  = request.form.get('inputImage')
    features  = request.form.get('inputFeatures')
    price  = request.form.get('inputPrice')
    quantity  = request.form.get('inputQuantity')

    newItem = Watches(brand = brand, model = model, image_url = image_url, features = features, price = price, quantity = quantity)
    db.session.add(newItem)

    db.session.commit()

    flash(f'"{brand} {model}" ürünü kaydedildi!', category='success')

    return redirect('/admin')


@app.route('/delete/<string:id>')
def delete_item(id):
    query = db.session.execute(db.select(Watches).filter_by(id=id)).scalar_one()

    db.session.delete(query)
    db.session.commit()

    return redirect('/admin')


#######################
# Giriş-Kayıt İşlemleri

@app.route('/login', methods=['POST'])
def login():
    login_username = request.form.get('inputUsername')
    print(login_username, file=sys.stderr)
    login_password = request.form.get('inputPassword')
    print(login_password, file=sys.stderr)

    return redirect('/account')

@app.route('/register', methods=['POST'])
def register():
    new_username = request.form.get('inputUsernameNew')
    print(new_username, file=sys.stderr)
    new_password = request.form.get('inputPasswordNew')
    print(new_password, file=sys.stderr)
    new_email = request.form.get('inputEmailNew')
    print(new_email, file=sys.stderr)

    newUser = Users(username = new_username, password = new_password, email = new_email)
    db.session.add(newUser)
    db.session.commit()

    return redirect('/account')


#######################
# Erkek-Kadın Saatleri (3'ü tek kodda birleşebilir)

@app.route('/watches-for-men')
def men_watches():
    query = Watches.query.filter(Watches.model.like('%Erkek%')).all()
    search_item = 'Erkek Saatleri'
    
    distinct_brands = db.session.query(Watches.brand.distinct()).order_by(Watches.brand).all()
    new_distinct_brands = []
    for brand in distinct_brands: new_distinct_brands.append(brand[0])

    return render_template('search.html', watches = query, search_item = search_item, search_len = len(query), brands = new_distinct_brands)


@app.route('/watches-for-women')
def women_watches():
    query = Watches.query.filter(Watches.model.like('%Kadın%')).all()
    search_item = 'Kadın Saatleri'
    
    distinct_brands = db.session.query(Watches.brand.distinct()).order_by(Watches.brand).all()
    new_distinct_brands = []
    for brand in distinct_brands: new_distinct_brands.append(brand[0])

    return render_template('search.html', watches = query, search_item = search_item, search_len = len(query), brands = new_distinct_brands)


@app.route('/smart-watches')
def smart_watches():
    query = Watches.query.filter(Watches.model.like('%Akıllı%')).all()
    search_item = 'Akıllı Saatler'
    
    distinct_brands = db.session.query(Watches.brand.distinct()).order_by(Watches.brand).all()
    new_distinct_brands = []
    for brand in distinct_brands: new_distinct_brands.append(brand[0])

    return render_template('search.html', watches = query, search_item = search_item, search_len = len(query), brands = new_distinct_brands)


if __name__ == "__main__":
    app.run(debug=True)