from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import Length, DataRequired, EqualTo, Email, ValidationError
from src.models import user
from src import db, app


class registration_form(FlaskForm):
    '''
    This class represents a registration form.
    '''
    name = StringField("Name", validators=[
                       DataRequired(), Length(min=3, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[
                             DataRequired(), Length(min=5, max=25)])
    confirm_password = PasswordField("Confirm Password", validators=[
                                     DataRequired(), EqualTo("password")])
    register = SubmitField("Register")

    # Check if email provided already exists.
    def validate_email(self, email):
        # Query the database
        with app.app_context():
            try:
                search_user = db.session.execute(
                    db.select(user).filter_by(email=email.data)).one()
            except:
                search_user = None

        if search_user:
            raise ValidationError(
                'This email is already taken, Please try another one!!')


class login_form(FlaskForm):
    '''
    This class represents a login form.
    '''
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    login = SubmitField("Login")
    remember_me = BooleanField('Remember me')


class post_form(FlaskForm):
    '''
    This class represents a form to create a new post.
    '''
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    post = SubmitField('Post')
