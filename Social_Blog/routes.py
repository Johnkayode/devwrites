from flask import render_template,url_for,flash,redirect,request
from Social_Blog import app,db,bcrypt
from Social_Blog.forms import RegistrationForm,LoginForm
from Social_Blog.models import User


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user = User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("You've been successfully registered, you can now log in.", 'success')
        return redirect(url_for('login'))
    else:
        flash('Login Unsuccessful, Please check username and password','danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            flash("You've been logged in", 'success-alert')
            return redirect(url_for('index'))
        else:
            flash('Wrong email or password', 'danger-alert')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route('/explore')
def explore():
    return render_template('explore.html')