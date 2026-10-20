from flask_wtf import FlaskForm 
from wtforms import SubmitField, StringField, PasswordField, FloatField
from wtforms.validators import InputRequired, EqualTo, Length

class RegistrationForm(FlaskForm):
    user_id = StringField("User id:", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    password2 = PasswordField("Confirm Password:", validators=[InputRequired(), EqualTo("password")])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    user_id = StringField("User id:", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    submit = SubmitField("Submit")

class AdminForm(FlaskForm):
    admin_id = StringField("Admin id:", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Submit")

class FeedbackForm(FlaskForm):
    feedback = StringField("Feedback:", validators=[InputRequired(), Length(5,500)])
    submit = SubmitField("Submit")

class AddForm(FlaskForm):
    item = StringField("Item Name:", validators=[InputRequired()])
    price = FloatField("Price of Item:", validators=[InputRequired()])
    category = StringField("Category of Item:", validators=[InputRequired()])
    submit = SubmitField("Submit")

class RemoveForm(FlaskForm):
    remove_item = StringField("Item to be removed:", validators=[InputRequired()])
    submit = SubmitField("Submit")