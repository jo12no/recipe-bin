from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileRequired, FileAllowed # image uploads
from flask_2019_app.models import user # for the registration form custom validation

class login_form(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

def validate_invitation_code(form, field):
	if field.data != "SECRET":
		raise ValidationError('Incorrect code')

class registration_form(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	
	invitation_code = StringField('Invitation Code', validators=[DataRequired(), validate_invitation_code])

	submit = SubmitField('Register')

	def validate_username(self, username):
		user_to_validate = user.query.filter_by(username=username.data).first()
		if user_to_validate is not None:
			raise ValidationError('Please use a different username.')

	def validate_email(self, email):
		user_to_validate = user.query.filter_by(email=email.data).first()
		if user_to_validate is not None:
			raise ValidationError('Please use a different email address.')

class publish_form(FlaskForm):
	title = StringField('Title', validators=[DataRequired()])
	ingredients = TextAreaField('Ingredients', validators=[DataRequired()])
	body = TextAreaField('Instructions', validators=[DataRequired()])
	image = FileField('Image', validators=[FileAllowed(['jpg', 'png'], 'Image only!')])
	tags = StringField('Tags')
	submit = SubmitField('Publish')

class edit_form(FlaskForm):
	title = StringField('Title', validators=[DataRequired()])
	ingredients = TextAreaField('Ingredients', validators=[DataRequired()])
	body = TextAreaField('Instructions', validators=[DataRequired()])
	image = FileField('Image', validators=[FileAllowed(['jpg', 'png'], 'Image only!')])
	tags = StringField('Tags')
	submit = SubmitField('Save')

class search_form(FlaskForm):
	search_term = StringField('Search', validators=[DataRequired()])
	submit = SubmitField('Search')