from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional
from src.models import Users

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max =16)])
    password = PasswordField('Password', validators=[DataRequired(),Length(min=5)])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken')

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')
	
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max =16)])
    spotifyid = StringField("")
    firstname = StringField('Firstname', validators=[Optional(), Length(min=1, max =16)])
    lastname = StringField('Lastname', validators=[Optional(), Length(min=1, max =16)])
    password = PasswordField(validators=[Optional(), Length(min=5)])
    confirm_password = PasswordField('Confirm Password',validators=[EqualTo('password')])
    save = SubmitField('Save')
    # def validate_username(self, usernames):
    #     user = Users.query.filter_by(username=usernames.data).first()
    #     if (user.username == usernames.data):
    #         if user:
    #             raise ValidationError('Sorry username is already taken')

# Search Form 
class SearchForm(FlaskForm):
	searched = StringField("Searched", validators=[DataRequired(), Length(min=1)])
	submit = SubmitField("Submit")
