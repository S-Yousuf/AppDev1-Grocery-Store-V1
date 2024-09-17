from flask import Flask, render_template, request, url_for, redirect, session, flash
from model import * 

# ==================================== Configuration ===================================== #

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mad1project.sqlite3"
app.config['SECRET_KEY'] = 'TheSecretKey'

db.init_app(app)
app.app_context().push()

# ====================================== Controller ======================================= #

@app.route("/")
def home():
  categories = Category.query.all()
  products = Products.query.all()  
  return render_template('home.html', categories=categories, products=products)

@app.route('/login', methods= ['GET', 'POST'])
def login():
  if 'user' in session:
    return redirect("/user_dashboard")
  if request.method == 'GET':
    return render_template('customer_login.html')
  elif request.method == 'POST':
    username = request.form["username"]
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()
    
    if user.password != password:
      flash("Password does not match!", "danger")
    elif not user:
      return redirect(url_for('register'))
    else:  
      session["user"] = username
      return redirect(url_for('Udashboard'))
      
# user Login if password incorrect


@app.route('/user_dashboard', methods=['GET', 'POST'])
def Udashboard():
  categories = Category.query.all()
  products = Products.query.all()
  if 'user' in session:
    user = User.query.filter_by(username = session["user"]).first()
    return render_template('user_dashboard.html', products=products, categories=categories,user = session["user"], signed = True)

@app.route('/logout', methods=[ 'GET','POST'])
def logout():
  if "user" in session:
    session.pop("user")
  return redirect(url_for('home'))

@app.route('/register', methods= ['GET', 'POST'])
def register():
    
  if request.method == 'GET':
    return render_template('register.html')
  
  if request.method == 'POST':
      username = request.form["username"]
      password = request.form["password"]
      new_user = User(username=username, password=password)
      db.session.add(new_user)
      db.session.commit()
      return redirect(url_for('login'))
  
''' --------------------------------- Search ------------------------------------'''  

@app.route('/search', methods=['GET'])
def search():
  q = request.args.get('q')
  query = '%'+q+'%'
  product = Products.query.filter(Products.p_name.like(query)).all()
  category = Category.query.filter(Category.c_name.like(query)).all()
  price = Products.query.filter(Products.rate.like(query)).all()
  date = Products.query.filter(Products.mfd.like(query)).all()

  return render_template('search_results.html', q = q, product = product, category=category, price = price, date=date)

''' ----------------------------------- Manager ---------------------------------'''

@app.route('/manager-login', methods=['GET', 'POST'])
def mlogin():
    if request.method == 'GET':  
      return render_template('manager_login.html')
    elif request.method == 'POST':
      username = request.form['username']
      password = request.form['password']

      if username == 'Admin' and password == 'password':
        session["manager"] = username
        return redirect('/manager_dashboard')       
      
    return redirect('/manager-login')      
    
@app.route('/manager_dashboard', methods= ['GET', 'POST'])
def Mdashboard():
  if "manager" in session:
    categories = Category.query.all()
    products = Products.query.all()
    return render_template('manager_dashboard.html', categories=categories, products=products)
  else:
    return render_template('home.html')


@app.route('/Mlogout', methods=[ 'GET','POST'])
def mlogout():
  if 'manager' in session:
    session.pop('manager')
  return redirect(url_for('home'))

'''------------------------- Category ----------------------- '''

@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
  if request.method == 'GET':
    return render_template('add_category.html')
  
  elif request.method == 'POST':
    name = request.form['name']
    category = Category(c_name = name)
    db.session.add(category)
    db.session.commit()

    return redirect('/manager_dashboard')

@app.route('/delete_category/<int:c_id>', methods=['GET', 'POST'])
def delete_category(c_id):
  category = Category.query.all()
  c_id = Category.query.get(c_id)
  if 'manager' in session:    
    if request.method == 'GET':
      return render_template('delete_category.html', c_id = c_id, category=category)
    else:
      if 'yes' in request.form:
        delete_products = Products.query.filter_by(section = c_id.c_id).all()
        for product in delete_products:
          db.session.delete(product)        
        db.session.delete(c_id)
        db.session.commit()        
        return redirect('/manager_dashboard')  
  return redirect('/manager-login')

@app.route('/edit_category/<int:c_id>', methods=['GET', 'POST'])
def edit_category(c_id):
  category = Category.query.filter_by(c_id=c_id).first()  
  if 'manager' in session:
    if request.method == 'GET':
      return render_template('edit_category.html', category=category)
    if request.method == 'POST':
      name = request.form['name']
      
      if name:
        category.c_name = name   
        db.session.commit() 
        return redirect('/manager_dashboard')
  return redirect('/manager-login')       

'''-------------------------------- Product ------------------------------'''

@app.route('/add_product/<int:c_id>', methods=['GET', 'POST'])
def add_product(c_id):
  if 'manager' in session:
    category = Category.query.all()
    c_id = Category.query.get(c_id)
    if request.method == 'GET':
      return render_template('add_product.html', category=category, c_id = c_id)
    
    if request.method == 'POST':
      p_name = request.form['p_name']
      mfd = request.form['mfd']
      rate = request.form['rate']
      unit = request.form['unit']
      stock = request.form['stock']
      section = request.form['c_name']
      product = Products(p_name = p_name, mfd = mfd, rate = rate, unit=unit, stock = stock, section=section)
      db.session.add(product)
      db.session.commit()
      return redirect('/manager_dashboard')    
  return redirect('/manager-login')

@app.route('/action/<int:p_id>',methods=['GET', 'POST'])
def edit_delete_product(p_id):
  product = Products.query.filter_by(p_id=p_id).first()
  if 'manager' in session:
    if request.method == 'GET':
      return render_template('actions.html', product=product)
    if request.method == 'POST':
      if 'Edit' in request.form:
        p_name = request.form['p_name']
        mfd = request.form['mfd']
        rate = request.form['rate']
        unit = request.form['unit']
        stock = request.form['stock']

        if p_name:
          product.p_name = p_name
        if rate:
          product.rate = rate
        if mfd:
          product.mfd = mfd
        if unit:
          product.unit = unit  
        if stock:
          product.stock = stock
        db.session.commit()
        return redirect('/manager_dashboard')
      
      if 'Delete' in request.form:  
        db.session.delete(product)
        db.session.commit()
        return redirect('/manager_dashboard')    

  return redirect('/manager-login')

''' --------------------------------- Cart -------------------------------------'''

@app.route('/addToCart/<int:p_id>', methods=['GET', 'POST'])
def addToCart(p_id):
  product = Products.query.get(p_id)
  category = Category.query.all()
  if 'user' in session:
    if request.method == 'GET':
      user = User.query.filter_by(username = session["user"]).first()
      u_id = user.u_id              
      return render_template('addToCart.html', p_id=p_id, product=product, category=category, user=user)

    if request.method == 'POST':
      user = User.query.filter_by(username = session["user"]).first()
      u_id = user.u_id
      quantity = int(request.form['quantity'])

      if quantity > product.stock:
        error = "You're ordering beyond the stock value"
        return render_template('addToCart.html', p_id=p_id, product=product, category=category, user=user, error=error)

      price = int(product.rate)
      cart_item = Cart.query.filter_by(u_id=u_id, p_id=p_id).first()

      if cart_item:
        cart_item.quantity += quantity
        cart_item.price = price
      else:
        cart_item = Cart(u_id=u_id, p_id=p_id, quantity=quantity, price = price)
        db.session.add(cart_item)

      db.session.commit()
      return redirect('/user_dashboard')
  return redirect('/')


@app.route('/cart', methods=['GET', 'POST'])
def view_cart():
  if 'user' in session:
    user = User.query.filter_by(username = session["user"]).first()
    u_id = user.u_id
    cart = Cart.query.filter_by(u_id=u_id).all()
    products = Products.query.all()

    if request.method == 'GET':
      return render_template('cart.html', cart=cart, products=products, u_id=u_id, user=user)
# checkout and delete products    
    if request.method == 'POST':   
      error = None   
      for item in cart:
        product = Products.query.get(item.p_id)
        if product:
          product.stock -= item.quantity
        db.session.delete(item)
      db.session.commit()
      return render_template('checkout.html', user=user)
    
  return redirect('/')

def stock(u_id):
  cart = Cart.query.filter_by(u_id = u_id).all()
  product = Products.query.get(cart.p_id)
  diff = product.stock - cart.quantity
  if diff < 0:
    return False
  else:
    return True
app.jinja_env.globals.update(stock=stock)


def get_grand_total(u_id):
    cart= Cart.query.filter_by(u_id = u_id).all()
    total = 0
    for item in cart:        
        subtotal = int(item.price ) * int(item.quantity)
        total += subtotal
    return total
app.jinja_env.globals.update(get_grand_total=get_grand_total)


@app.route('/review/<int:p_id>', methods=['GET', 'POST'])
def edit_delete_cart(p_id):
  cart = Cart.query.filter_by(p_id=p_id).first()
  product = Products.query.get(p_id) 
  if 'user' in session:
    if request.method == 'GET':
      total = product.rate * cart.quantity
      return render_template('edit_delete_cart.html', cart=cart,product=product, total=total)
    if request.method == 'POST':
      if 'Edit' in request.form:
        quantity = request.form['quantity']
        if quantity:
          cart.quantity = quantity
        db.session.commit()
        
      if 'Delete' in request.form:
        db.session.delete(cart)
        db.session.commit()
      return redirect('/cart')
  return redirect('/')

# =========================================== Run ========================================== #

if __name__ == '__main__':
  db.create_all()
  app.run(debug=True)

