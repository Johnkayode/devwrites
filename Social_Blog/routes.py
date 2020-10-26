import os
import secrets

from flask import abort
from flask import current_app as app
from flask import (flash, jsonify, make_response, redirect, render_template,
                   request, send_from_directory, url_for)
from flask_cors import cross_origin
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from PIL import Image
from sqlalchemy import func

from . import bcrypt, db, mail
from .forms import (CommentForm, LoginForm, PostForm, RegistrationForm,
                    RequestResetForm, ResetPasswordForm, UpdateProfileForm)
from .models import Comment, Follow, Post, User


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/home")
@login_required
def home():
    show_followed = ""

    show_followed = request.cookies.get("show_followed")
    if show_followed == "1":
        query_ = Post.query.filter_by(author=current_user)
        query = current_user.followed_posts
        active = "followed"
    else:
        query = Post.query
        active = "all"
    page = request.args.get("page", 1, type=int)
    posts_ = Post.query.order_by(Post.date_posted.desc()).all()
    posts = query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    if len(posts_) >= 5:
        top_articles = posts_[0:5]
    else:
        top_articles = posts_
    users = (
        User.query.outerjoin(Post).group_by(User.id).order_by(func.count().desc()).all()
    )
    if len(users) >= 5:
        users = users[0:5]

    return render_template(
        "home.html", posts=posts, users=users, top_articles=top_articles, active=active
    )


@app.route("/home/all")
@login_required
def show_all():
    resp = make_response(redirect(url_for("home")))
    resp.set_cookie("show_followed", "", max_age=30 * 24 * 60 * 60)
    return resp


@app.route("/home/followed")
@login_required
def show_followed():
    resp = make_response(redirect(url_for("home")))
    resp.set_cookie("show_followed", "1", max_age=30 * 24 * 60 * 60)
    return resp


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data, email=form.email.data, password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash(
            "You've been successfully registered, you can now log in.", "success-alert"
        )
        return redirect(url_for("login"))
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            flash("You've been logged in", "success-alert")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Wrong email or password", "danger-alert")
    return render_template("login.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You've been logged out", "success-alert")
    return redirect(url_for("login"))


def save_picture(form_picture, output_size=(125, 125)):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.config["UPLOADED_PHOTOS_DEST"], picture_fn)

    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn


@app.route("/<string:user>", methods=["GET", "POST"])
@login_required
def profile(user):
    user = User.query.filter_by(username=user).first()
    if user is None:
        abort(404)
    article = len(user.posts)
    contributions = len(user.posts) + user.comments.count()
    image_file = url_for("static", filename="images/" + user.image_file)
    page = request.args.get("page", 1, type=int)
    posts = (
        Post.query.filter_by(author=user)
        .order_by(Post.date_posted.desc())
        .paginate(page=page, per_page=5)
    )

    return render_template(
        "profile.html",
        posts=posts,
        user=user,
        image_file=image_file,
        article=article,
        contributions=contributions,
    )


@app.route("/<string:user>/update", methods=["GET", "POST"])
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
            flash("Profile successfully updated", "success-alert")
            return redirect(url_for("profile", user=current_user.username))
        elif request.method == "GET":
            form.username.data = current_user.username
            form.email.data = current_user.email
            form.bio.data = current_user.bio
        return render_template("update.html", form=form)
    else:
        abort(403)


@app.route("/<string:user>/delete", methods=["GET", "POST"])
@login_required
def delete_account(user):
    if user == current_user.username:
        user = User.query.filter_by(username=user).first()
        db.session.delete(user)
        db.session.commit()
        flash("Your account has been deleted", "success-alert")
        return redirect(url_for("register"))
    else:
        abort(403)


@app.route("/explore")
def explore():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    if len(posts) >= 5:
        top_articles = posts[0:5]
    else:
        top_articles = posts
    users = (
        User.query.outerjoin(Post).group_by(User.id).order_by(func.count().desc()).all()
    )
    if len(users) >= 5:
        users = users[0:5]
    return render_template(
        "explore.html", posts=posts, users=users, top_articles=top_articles
    )


@app.route("/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data, content=form.content.data, author=current_user
        )
        db.session.add(post)
        post.create_slug()
        db.session.commit()
        flash("You've sucessfully published your article", "success-alert")
        return redirect(url_for("home"))
    return render_template(
        "new_post.html", title="New Article", form=form, legend="New Article"
    )


@app.route("/upload_attachment", methods=["GET", "POST"])
def upload_attachment():
    file = request.files["file"]
    _ = save_picture(file, output_size=(1000, 1000))
    file_url = url_for("serve_photo", filename=_, _external=True)
    return jsonify({"url": file_url})


@app.route("/photos/<filename>")
def serve_photo(filename):
    return send_from_directory(app.config["UPLOADED_PHOTOS_DEST"], filename)


@app.route("/<post_author>/<post_slug>", methods=["GET", "POST"])
@login_required
def post(post_author, post_slug):
    post = Post.query.filter_by(slug=post_slug).first()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            body=form.body.data, post=post, author=current_user._get_current_object()
        )
        db.session.add(comment)
        db.session.commit()
        return redirect(
            url_for("post", post_author=post.author.username, post_slug=post.slug)
        )
    comments = post.comments.order_by(Comment.date_posted.asc()).all()
    return render_template(
        "post.html", title=post.title, post=post, comments=comments, form=form
    )


@app.route("/<post_id>/comment/<id>/delete", methods=["GET", "POST"])
@login_required
def delete_comment(id, post_id):
    post = Post.query.get_or_404(post_id)
    comment = Comment.query.get_or_404(id)
    if current_user.username == comment.author.username:

        db.session.delete(comment)
        db.session.commit()

        return redirect(
            url_for("post", post_author=post.author.username, post_slug=post.slug)
        )
    else:
        abort(403)


@app.route("/<post_author>/<post_slug>/update", methods=["GET", "POST"])
@login_required
def update_post(post_author, post_slug):
    post = Post.query.filter_by(slug=post_slug).first()
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your article has been updated!", "success-alert")
        return redirect(
            url_for("post", post_author=post.author.username, post_slug=post.slug)
        )
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template(
        "new_post.html", title="Update Article", form=form, legend="Update Article"
    )


@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your article has been deleted!", "success-alert")
    return redirect(url_for("home"))


@app.route("/<username>/follow")
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("Invalid User", "danger-alert")
    if current_user.is_following(user):
        flash("You are already following this user", "danger-alert")
        return redirect(url_for("profile", user=username))
    current_user.follow(user)
    flash("You are now following this user", "success-alert")
    return redirect(url_for("profile", user=username))


@app.route("/<username>/unfollow")
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("Invalid User", "danger-alert")
    if not current_user.is_following(user):
        flash("You were not following this user", "danger-alert")
        return redirect(url_for("profile", user=username))
    current_user.unfollow(user)

    flash("You have unfollowed this user", "success-alert")
    return redirect(url_for("profile", user=username))


@app.route("/<user>/followers")
@login_required
def followers(user):
    user = User.query.filter_by(username=user).first()
    users = []

    for i in user.followers:
        id = i.follower_id
        user_person = User.query.filter_by(id=id).first()
        users.append(user_person)
    if user.followers.count() == 0:
        return redirect(url_for("profile", user=user.username))
    return render_template("followers.html", users=users)


@app.route("/<user>/following")
@login_required
def followed(user):
    user = User.query.filter_by(username=user).first()
    users = []
    for i in user.followed:
        id = i.followed_id
        user_person = User.query.filter_by(id=id).first()
        users.append(user_person)
    if user.followed.count() == 0:
        return redirect(url_for("profile", user=user.username))
    return render_template("followers.html", users=users)


@app.route("/theproject")
@login_required
def project():
    return render_template("project.html")


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        "Password Reset Request",
        sender="noreply@devswrite.com",
        recipients=[user.email],
    )
    msg.body = f"""To reset your password, visit:
    {url_for('reset_token',token=token, _external=True)}

    If you didn't make this request, please ignore this email
    """
    mail.send(msg)


@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent to reset your password", "info")
        return redirect(url_for("login"))
    return render_template("reset_request.html", title="Reset Password", form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    user = User.verify_reset_token(token)
    if user is None:
        flash("Invalid token", "warning")
        return redirect(url_for("reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated! You are now able to log in", "success")
        return redirect(url_for("login"))
    return render_template("reset_token.html", title="Reset Password", form=form)
