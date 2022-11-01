from src.models import user, post
from src import app, db, bcrypt
from src.forms import registration_form, login_form, post_form
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import logout_user, current_user, login_user, login_required, login_manager


@app.route("/")
def home():
    posts = []
    with app.app_context():
        items = db.session.execute(db.select(post)).all()
        for item in items:
            posts.append((item[0].id, item[0].title, item[0].content[:20],
                         item[0].author.name, item[0].date_posted.date()))
    return render_template("home.html", posts=posts)


@app.route("/login", methods=["GET", "POST"])
def login():
    '''
        This route corresponds to the login of an user.
        This compares credentials with the pre-registerd credentials.
        Upon failure, user is flashed with appropriate message else, user is redirected to home page
    '''
    # If the user is already logged in then rediect to home page.
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = login_form()

    # Validating the form aganist the values entered by the user.
    if form.validate_on_submit():
        # Upon validation taking the data from the form
        email = form.email.data
        password = form.password.data

        # Check if the user is a registered earlier.
        with app.app_context():
            try:
                search_user = db.session.execute(
                    db.select(user).filter_by(email=email)).scalar()
            except:
                search_user = None

        # checking entered password aganist the saved password in db
        try:
            password_flag = bcrypt.check_password_hash(
                search_user.password, password)
        except:
            password_flag = False

        # If the users credentials are authenticated, login the user else
        # Prompt with an error message.
        if search_user and password_flag:
            login_user(search_user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash("You have logged in successfully!!", "success")
            if next_page:
                return redirect(next_page)
            return redirect(url_for('home'))
        else:
            flash("Please check the email and Password", "fail")
            return redirect(url_for('login'))

    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    '''
        This route corresponds to the registration of new user. 
        The data of the new users is validated and stored in the database. 
        Upon failure to save the data, the user is flashed with the appropriate message. 
    '''

    # If the user is already logged in then rediect to home page.
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = registration_form()

    # Validating the form aganist the values entered by the user.
    if form.validate_on_submit():
        # Upon validation taking the data from the form
        name = form.name.data
        email = form.email.data
        password = form.password.data

        # Instead of saving the plain text password, hash the password.
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        # Creating an user object to save.
        new_user = user(name=name, email=email, password=password_hash)

        # Saving to the database.
        with app.app_context():
            db.session.add(new_user)
            db.session.commit()

        flash('You have successfully registered!!', 'success')
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/logout")
@login_required
def logout():
    '''
    This route corresponds to the logging out of an user.
    '''
    print(current_user)
    logout_user()
    try:
        print(current_user)
    except:
        print("wrong")
    return redirect(url_for('home'))


@app.route("/about")
def about():
    return render_template('about.html', about_page=True)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_article():
    form = post_form()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_post = post(title=title, content=content, author=current_user)
        with app.app_context():
            db.session.add(new_post)
            db.session.commit()

        flash('You have successfully posted an article!', 'success')
        return redirect(url_for('home'))

    return render_template('create.html', form=form, form_title='Write an article')


@app.route('/post/<int:post_id>')
def article(post_id):
    with app.app_context():
        single_post = db.get_or_404(post, post_id)
        post_author = single_post.author

    print(post_author, post_author.name)

    return render_template('article.html', post=single_post, author=post_author)


@app.route('/post/update-article/<int:post_id>', methods=['GET', 'POST'])
@login_required
def update_article(post_id):
    with app.app_context():
        update_post = db.get_or_404(post, post_id)

        if update_post.author != current_user:
            abort(403)

    form = post_form()

    if form.validate_on_submit():

        with app.app_context():
            update_post.title = form.title.data
            update_post.content = form.content.data
            db.session.commit()

        flash('Your post has been updated!', 'success')
        return redirect(url_for('article', post_id=update_post.id))

    elif request.method == 'GET':
        form.title.data = update_post.title
        form.content.data = update_post.content

    return render_template('create.html', form_title='Update an article', form=form)


@app.route('/post/delete-article/<int:post_id>', methods=['GET', 'POST'])
@login_required
def delete_article(post_id):
    with app.app_context():
        delete_post = db.get_or_404(post, post_id)

        if delete_post.author != current_user:
            abort(403)

        db.session.delete(delete_post)
        db.session.commit()

    flash('your post has been deleted!', 'success')
    return redirect(url_for("home"))
