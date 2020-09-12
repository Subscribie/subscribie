from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    FloatField,
    FieldList,
    FileField,
    validators,
    BooleanField,
    TextField,
    HiddenField,
    TextAreaField,
    IntegerField,
)
from wtforms.validators import Optional, DataRequired, Email as EmailValid
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_uploads import UploadSet, IMAGES


class StripWhitespaceForm(FlaskForm):
    class Meta:
        def bind_field(self, form, unbound_field, options):
            filters = unbound_field.kwargs.get("filters", [])
            if unbound_field.field_class is not FieldList:
                filters.append(strip_whitespace)
            return unbound_field.bind(form=form, filters=filters, **options)


def strip_whitespace(value):
    if value is not None and hasattr(value, "strip"):
        return value.strip()
    return value


class PlansForm(StripWhitespaceForm):
    email = TextField("Email", [validators.Email(), validators.DataRequired()])
    title = FieldList(StringField("Title", [validators.DataRequired()]), min_entries=1)
    company_name = TextField("Company Name")
    slogan = TextField("Slogan")
    instant_payment = FieldList(
        TextField("Up-Front Payment", default=False), min_entries=1
    )
    uuid = FieldList(StringField(), min_entries=1)
    subscription = FieldList(TextField("Subscription", default=False), min_entries=1)
    note_to_seller_required = FieldList(TextField("Require note from customer", default=False), min_entries=1)
    # Allow seller to say what additional information they need
    note_to_buyer_message = FieldList(TextAreaField(u'Note to buyer', [validators.optional(), validators.length(max=500)]))
    days_before_first_charge = FieldList(StringField("Days before first charge"))
    sell_price = FieldList(
        FloatField("Up-front Price", [validators.optional()]), min_entries=1
    )
    interval_amount = FieldList(
        FloatField("Reccuring Amount", [validators.optional()]), min_entries=1
    )
    interval_unit = FieldList(
        StringField("Interval Unit", [validators.optional()]), min_entries=1
    )
    selling_points = FieldList(
        FieldList(
            StringField("Unique Selling Point", [validators.DataRequired()]),
            min_entries=1,
        ),
        min_entries=1,
    )
    images = UploadSet("images", IMAGES)
    image = FieldList(
        FileField(validators=[FileAllowed(images, "Images only!")]), min_entries=1
    )
    position = FieldList(IntegerField("Position", [validators.optional()], default=0))


class ChoiceGroupForm(FlaskForm):
    title = StringField("title", validators=[DataRequired()])

class OptionForm(FlaskForm):
    title = StringField("title", validators=[DataRequired()])

class LoginForm(FlaskForm):
    email = StringField("email", validators=[DataRequired(), EmailValid()])

class PasswordLoginForm(FlaskForm):
    email = StringField("email", validators=[DataRequired(), EmailValid()])
    password = StringField("password", validators=[DataRequired()])

class SubscriberForgotPasswordForm(FlaskForm):
    email = StringField("email", validators=[DataRequired(), EmailValid()])

class SubscriberResetPasswordForm(FlaskForm):
    token = StringField("token", validators=[DataRequired()])
    password = StringField("password", validators=[DataRequired()])

class ForgotPasswordForm(FlaskForm):
    email = StringField("email", validators=[DataRequired(), EmailValid()])
    
class ForgotPasswordResetPasswordForm(FlaskForm):
    token = StringField("token", validators=[DataRequired()])
    password = StringField("password", validators=[DataRequired()])


class CustomerForm(FlaskForm):
    given_name = StringField("given_name", validators=[DataRequired()])
    family_name = StringField("family_name", validators=[DataRequired()])
    mobile = StringField("mobile", validators=[DataRequired()])
    email = StringField("email", validators=[DataRequired()])
    address_line_one = StringField("address_line_one", validators=[DataRequired()])
    city = StringField("city", validators=[DataRequired()])
    postcode = StringField("postcode", validators=[DataRequired()])
    note_to_seller = StringField("note_to_seller", validators=[Optional()])
    is_iframe = HiddenField("is_iframe")


class GocardlessConnectForm(FlaskForm):
    access_token = StringField("access_token", validators=[DataRequired()])


class StripeConnectForm(FlaskForm):
    publishable_key = StringField("publishable_key", validators=[DataRequired()])
    secret_key = StringField("secret_key", validators=[DataRequired()])


class GoogleTagManagerConnectForm(FlaskForm):
    container_id = StringField("container_id", validators=[DataRequired()])


class TawkConnectForm(FlaskForm):
    property_id = StringField("property_id", validators=[DataRequired()])

class ChangePasswordForm(FlaskForm):
    password = StringField("password", validators=[DataRequired()])
    
class ChangeEmailForm(FlaskForm):
    email = StringField("password", validators=[DataRequired(), EmailValid()])

class AddShopAdminForm(FlaskForm):
    email = StringField("password", validators=[DataRequired(), EmailValid()])
    password = StringField("password", validators=[DataRequired()])

class UploadLogoForm(StripWhitespaceForm):
    images = UploadSet("images", IMAGES)
    image = FileField(validators=[FileAllowed(images, "Images only!")])
