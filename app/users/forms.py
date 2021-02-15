from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from app.models import User


class SignUpForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(),
                                           Length(min=2, max=20,
                                                  message="Name must be minimum 4 characters long.")])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(),
                                                 EqualTo("password")])
    submit = SubmitField("Sign up")
    
    def validate_name(self, name):
        user = User.query.filter_by(name=name.data).first()
        if user:
            raise ValidationError("The user with this name already exists!")

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError("The user with this email already exists!")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log in")
    

class RequestResetForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    submit = SubmitField("Reset Password")

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is None:
            raise ValidationError("There's no account with that email.")
        

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(),
                                                 EqualTo("password")])
    submit = SubmitField("Reset Password")


class ChangePassword(FlaskForm):
    new_password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(),
                                                 EqualTo("new_password")])
    submit1 = SubmitField("Update Password")


class ChangeName(FlaskForm):
    new_name = StringField("Evgeny", validators=[Length(min=2, max=20)])
    submit2 = SubmitField("Update")

    def validate_name(self, field):
        name = User.query.filter_by(name=field.data).first()
        if name:
            raise ValidationError("The user with this name already exists!")


class DeleteAccount(FlaskForm):
    submit3 = SubmitField("Yes, delete my account")


class ContactForm(FlaskForm):
    name = StringField("Name *", validators=[DataRequired()])
    email = EmailField("Email *", validators=[DataRequired()])
    message = TextAreaField("Message *", validators=[DataRequired(),
                                           Length(min=20, max=300,
                                                  message="Message must be minimum 20 characters long.")]
                          )
    subject = StringField("Subject *", validators=[DataRequired()])
    submit = SubmitField("Send")
