from flask import Flask, render_template, redirect, flash, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import flask_login 
from flask_login import LoginManager, UserMixin, login_required, current_user
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'Library'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------TABLES-----------------------------
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(128), nullable=True)
    Email = db.Column(db.String(128), unique=True, nullable=True)
    Password = db.Column(db.String(128), nullable=True)

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Sec_Name = db.Column(db.String(128), nullable=True)
    Sec_Description = db.Column(db.Text(), nullable=True)
    Sec_Date = db.Column(db.Date(), nullable=True)

class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Book_name = db.Column(db.String(128), nullable=True)
    Book_content = db.Column(db.String(512), nullable=True)
    Book_author = db.Column(db.String(128), nullable=True)
    Date_issued = db.Column(db.Date(), nullable=True)
    Return_date = db.Column(db.Date(), nullable=True)


#------------------APP INTERFACE--------------------------
@app.route('/')
def index():
    return render_template('home.html')


@app.route('/userlist')
def userlist():
    users = Users.query.all()
    return render_template('userlist.html', users=users)


#--------------------USER--------------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    name = None
    email = None
    password1 = None
    password2 = None
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        try:
            if password1 == password2:
                password = password1
                new_user = Users(Name=name, Email=email, Password=password)
                db.session.add(new_user)
                db.session.commit()
                flash('User added successfully')
                return render_template('user_dashboard.html', user=new_user)
            else:
                flash('Passwords donot match, please try again...')
                return render_template('signup.html')
        except Exception as e:
            flash(f'An error occured: {str(e)}')
            return render_template('signup.html')
    return render_template('signup.html')


@app.route('/userlogin', methods=['POST', 'GET'])
def login():
    email = None
    password = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user_to_check = Users.query.filter_by(Email=email).first()
            if user_to_check is None:
                flash('No user was found...')
            elif user_to_check.Password != password:
                flash('Incorrect password, please try again...')
            else:
                if user_to_check.Email == 'admin@mail.com':
                    flash('Login successfull!')
                    return redirect(url_for('admin'))
                else:
                    flash('Login successfull!')
                    return render_template('user_dashboard.html', user=user_to_check)
        except Exception as e:
            flash(f'An error occured: {str(e)}')
            return redirect(url_for("index"))
    return render_template('userlogin.html')


@app.route('/logout')
@login_required
def logout():
    flask_login.logout_user()
    flash('Logout successful')
    return redirect(url_for('index'))


@app.route('/user/delete/<int:id>')
@login_required
def deleteuser(id):
    user = Users.query.get_or_404(id)
    if current_user.id == user.id:
        try:
            db.session.delete(user)
            db.session.commit()
            flash('User has been deleted successfully. We are sad to see you leave')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'An error has occured: {str(e)}')
            return redirect(url_for("userlist"))
    else:
        flash('You are unatuhorized to access this page')
        return redirect(url_for('unauthorized'))      


#----------------------------ADMIN--------------------------
@app.route('/admin/dashboard')
def admin():
    return render_template('admin.html')


#----------------------ERROR PAGES--------------------------
@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404



if __name__ == '__main__':
    app.run(debug=True)