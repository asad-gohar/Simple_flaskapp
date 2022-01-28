import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from sqlalchemy import or_

from flask_login import login_user, logout_user, current_user,LoginManager,UserMixin
import datetime 
import shutil
from flask_bcrypt import Bcrypt 
from flask_uploads import configure_uploads, UploadSet, DOCUMENTS
from flask_admin import Admin 
from flask_admin.contrib.sqla import ModelView

# print("found")
# except:
#     print("not found d")

myApp = Flask(__name__)
myApp.secret_key = os.urandom(24)


project_dir = os.path.abspath(os.path.dirname(__file__))








database_file = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))
myApp.config["SQLALCHEMY_DATABASE_URI"] = database_file
myApp.config[" SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(myApp)



myApp.config['UPLOADED_DOCUMENTS_DEST'] = "upload"
myApp.config['UPLOADED_DOCUMENTS_ALLOW'] = ['xlsx', 'xls', 'csv', 'pdf', 'zip', 'png','txt', 'jpg','jpeg', 'doc', 'docx', 'gif']
docs = UploadSet('documents', DOCUMENTS)
configure_uploads(myApp, docs)


bcrypt = Bcrypt(myApp)
login_manager=LoginManager()
login_manager.init_app(myApp)
admin = Admin(myApp)


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    product= db.relationship("Products", backref="product")
    


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.String(100), nullable=False)
    dated_updated = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))




# db.create_all()
admin.add_view(ModelView(User,db.session))
admin.add_view(ModelView(Category,db.session))
admin.add_view(ModelView(Products,db.session))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))






@myApp.route("/")
def home():
    return redirect(url_for("login"))



@myApp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard")) 
    if request.method == 'POST':
        Email = request.form["Email"]
        password1 = request.form["password"]
        rememberme = request.form["rememberme"]

        user = User.query.filter_by(email=Email).first()
        if user:
            if bcrypt.check_password_hash(user.password, password1):
                print(rememberme)
                remember = False
                if rememberme == "True":
                    remember = True
                print(remember)
                login_user(load_user(user.id), remember)
                return redirect(url_for("dashboard"))
             
            else:

                return render_template("login.html", msg="Invalid Passowrd")
        else:
            return render_template("login.html", msg1="Invalid Email")

    return render_template("login.html")




@myApp.route('/signup', methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        user = User()
        user1 = User.query.all()
        email = request.form["Email"]
        user.name = request.form["name"]
        user.password = bcrypt.generate_password_hash(request.form["password"]).decode('utf-8')
        # user.u_PasswordConfirmed = request.form["confirm"]

        for u in user1:
            if u.email == email:
                return render_template("signup.html", email=email,user="", error="Email Exist",req="required",action="/signup",hidep="d-none",read="")
        user.email = email

        db.session.add(user)
        db.session.commit()
        flash('Sign Up Successful')
        return redirect(url_for("login"))
        

    return render_template("signup.html")


@myApp.route('/dashboard')
def dashboard():
    if current_user.is_authenticated:
        category=Category.query.all()
        product=Products.query.all()
        return render_template("dashboard.html",category=category,product=product)
    else:
        return redirect(url_for("login"))

@myApp.route('/add_category',methods=["POST", "GET"])
def add_category():
    if current_user.is_authenticated:
        if request.method == "POST":
            c = Category()
            c.name=request.form["name"]
            db.session.add(c)
            db.session.commit()
            return redirect(url_for("dashboard"))

@myApp.route('/add_product',methods=["POST", "GET"])
def add_product():
    if current_user.is_authenticated:
        if request.method == "POST":
            
            
            category_id=request.form.getlist("category")
            filename = docs.save(request.files["image"],"images",request.files["image"].filename)
            if filename:
                for i in category_id:
                    p = Products()
                    print(i)
                    p.title=request.form["title"]
                    p.description=request.form["description"]
                    p.price=request.form["price"]
                    p.date_added=datetime.datetime.now()
                    p.dated_updated=datetime.datetime.now()
                    p.category_id=i
                    p.image = docs.url(filename)
                    db.session.add(p)
                    print("yes")
            db.session.commit()
                

  
            return redirect(url_for("dashboard"))



            
        
    else:
        return redirect(url_for("login"))


@myApp.route('/logout')
def log_out():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    # myApp.run(host = '0.0.0.0',debug=True)
    myApp.run(debug=True)
