import os
import secrets
from PIL import Image
from flask import render_template,url_for,flash,redirect, request
from Social_Blog import app,db,bcrypt
from Social_Blog.forms import RegistrationForm, LoginForm, UpdateProfileForm
from Social_Blog.models import User, Post
from flask_login import login_user, logout_user, current_user, login_required

posts = [
    {'author':'nerd_thejohn',
    'title':'Igbo Culture',
    'content': 'The Igbo people are one of the largest ethnic groups in Africa,\
        originated  present-day South-Central South-Eastern Nigeria. There have been different speculations about the origin of the Igbo people.\
        Before the British colonization, the Igbo people were a politically fragmented group until i slapped the shit ou t idni idnrfik',
    'date_posted': '7th June, 2020'},
    { 'author':'Sc_mofeoluwa',
    'title':'Yoruba Culture',
    'content': 'The Yoruba people are one of the largest ethnic groups in Africa,\
        originated  present-day South-Central South-Eastern Nigeria. There have been different speculations about the origin of the Igbo people.\
        Before the British colonization, the Igbo people were a politically fragmented group until i slapped the shit ou t idni idnrfik',
    'date_posted': '8th June, 2020'}


]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
@login_required
def home():
    return render_template('home.html',posts=posts)

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("You've been successfully registered, you can now log in.", 'success-alert')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash("You've been logged in", 'success-alert')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Wrong email or password', 'danger-alert')
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn



@app.route('/users/<string:user>', methods=['GET','POST'])
@login_required
def profile(user):
    
    image_file = url_for('static',filename='images/'+ current_user.image_file)
    user = User.query.filter_by(username=user).first()
    article= len(user.posts)
    return render_template('profile.html',posts=posts,user=user,image_file=image_file, article=article)

@app.route('/users/<string:user>/update',methods=['GET','POST'])
@login_required
def update(user):
    if user == current_user.username:
        form = UpdateProfileForm()
        if form.validate_on_submit():
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.image_file = picture_file
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.bio = form.bio.data
            db.session.commit()
            flash('Profile successfully updated','success-alert')
            return redirect(url_for('profile',user=current_user.username))
        elif request.method == 'GET':
            form.username.data = current_user.username
            form.email.data = current_user.email
        return render_template('update.html',form=form)
    else:
        return redirect(url_for('profile',user=user))

@app.route('/explore')
def explore():
    return render_template('explore.html',posts=posts)