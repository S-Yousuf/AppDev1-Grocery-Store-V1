from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# One to Many relationship between Category and Product
# One product can belong to one Category, but one Category may have several products

class Category(db.Model):
  c_id = db.Column(db.Integer(), primary_key=True, autoincrement= True)
  c_name = db.Column(db.String(50), nullable=False)
  relation = db.relationship('Products', backref='item')
  
  def __repr__(self):
    return f"{self.c_name}"


class Products(db.Model):
  p_id = db.Column(db.Integer(), primary_key=True, autoincrement= True)
  p_name = db.Column(db.String(50), nullable=False)
  mfd = db.Column(db.String(10)) 
  unit = db.Column(db.String(50), nullable=False)
  rate = db.Column(db.Integer(), nullable=False)
  stock = db.Column(db.Integer(), nullable=False)
  section = db.Column(db.Integer(), db.ForeignKey("category.c_id"))
  
  def __repr__(self):
    return f"{self.p_name}"


class User(db.Model):
  u_id = db.Column(db.Integer(), primary_key=True, autoincrement= True)
  username = db.Column(db.String(50), nullable=False, unique=True)
  password = db.Column(db.String(50), nullable=False)
  
  def __repr__(self):
    return f"<User {self.name}>"

class Cart(db.Model):
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  u_id = db.Column(db.Integer, nullable=False)
  p_id = db.Column(db.Integer, nullable=False)
  quantity = db.Column(db.Integer())
  price = db.Column(db.Integer)
  grand_total = db.Column(db.Integer)