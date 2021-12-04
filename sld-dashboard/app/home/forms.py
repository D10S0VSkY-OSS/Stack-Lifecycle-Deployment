# -*- encoding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import validators
from wtforms import StringField, BooleanField, TextAreaField, TextField, PasswordField, FieldList, FormField, SelectMultipleField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Email, DataRequired

# login and registration


class StackForm(FlaskForm):
    name = StringField('Name', [
        validators.length(min=4, max=50, message='Name out of reange.'),
        validators.DataRequired(message='Name requerid.')
    ])
    git = StringField('Git', [
        validators.length(min=4, max=250, message='Git out of reange.'),
        validators.DataRequired(message='Git requerid.')
    ])
    branch = StringField('Branch', [
        validators.length(min=2, max=250, message='Branch out of reange.'),
        validators.DataRequired(message='Branch requerid.')
    ])
    #squad_access = FieldList(StringField('squads'), min_entries=1)
    squad_access = TextAreaField('Squad Access (* share with everyone or pass a list: squad1, squad2)', default='*', render_kw={'rows': 1})

    tf_version = StringField('tf version', [
        validators.length(min=4, max=10, message='tf version out of reange.'),
        validators.DataRequired(message='tf version requerid.')
    ])
    description = TextAreaField('Description', [
        validators.DataRequired(message='The description is required.')
    ], render_kw={'rows': 5})
    squad_access_edit = StringField('Squad Access (* share with everyone or pass a list: squad1, squad2)', render_kw={'rows': 1})
    description_edit = StringField('Description', render_kw={'rows': 1})


class DeployForm(FlaskForm):
    deploy_name = StringField('Deploy Name', [
        validators.length(min=4, max=50, message='Name out of reange.'),
        validators.DataRequired(message='Name requerid.')
    ])
    squad = StringField('Squad', [
        validators.length(min=4, max=50, message='Squad out of reange.'),
        validators.DataRequired(message='Squad requerid.')
    ])
    stack_name = StringField('Stack Name', [
        validators.length(min=4, max=50, message='stack out of reange.'),
        validators.DataRequired(message='Stack requerid.')
    ])
    environment = StringField('Environment', [
        validators.length(min=2, max=250, message='Branch out of reange.'),
        validators.DataRequired(message='Environment requerid.')
    ])
    start_time = StringField('Start Time', [
        validators.length(min=3, max=5, message='Time out of reange.'),
    ])
    destroy_time = StringField('Destroy Time', [
        validators.length(min=3, max=5, message='Time out of reange.'),
    ])
    environment = StringField('Environment', [
        validators.length(min=2, max=250, message='Branch out of reange.'),
        validators.DataRequired(message='Environment requerid.')
    ])
    variables = TextAreaField('Variables', render_kw={'rows': 5})


class UserForm(FlaskForm):
    role = ['yoda', 'darth_vader', 'stormtrooper', 'R2-D2', 'grogu']
    username = StringField('Username', [
        validators.length(min=4, max=50),
    ])
    fullname = StringField('Fullname', [
        validators.length(min=4, max=50),
    ])
    email = EmailField('Email', [
        validators.length(min=6, max=100),
        validators.Required(message='The email is required.'),
        validators.Email(message='Enter a valid email.')
    ])
    squad = StringField('Squad', [
        validators.length(min=4, max=50),
        validators.Required('The squad name is required.'),
    ])
    password = PasswordField(
        'Password', [
            validators.length(min=8, max=50),
            validators.Required('The password is required.'),
            validators.EqualTo(
                'confirm_password',
                message='The password does not match.'
            ),
        ]
    )
    confirm_password = PasswordField('Confirm password')
    privilege = BooleanField('', [
    ])
    master = BooleanField('', [
    ])
    is_active = BooleanField('', [
    ])


class AwsForm(FlaskForm):
    squad = StringField('Squad *', [
        validators.length(min=4, max=50, message='Squad out of reange.'),
        validators.DataRequired(message='Squad Name requerid.')
    ])
    access_key_id = StringField('Access_key_id *', [
        validators.length(
            min=4, max=50, message='Access key id out of reange.'),
        validators.DataRequired(message='Access_key_id requerid.')
    ])
    secret_access_key = StringField('Secret_access_key *', [
        validators.length(
            min=4, max=50, message='Secret Access Key out of reange.'),
        validators.DataRequired(message='Secret_access_key.')
    ])
    default_region = StringField('Default_region *', [
        validators.length(
            min=4, max=50, message='Default Region out of reange.'),
        validators.DataRequired(message='default_region.')
    ])
    profile_name = StringField('Profile_name', [
        validators.length(
            min=4, max=50, message='profile_name out of reange.'),
    ])
    role_arn = StringField('Role_arn', [
        validators.length(
            min=4, max=50, message='Role arn out of reange.'),
    ])
    source_profile = StringField('Source_profile', [
        validators.length(
            min=4, max=50, message='source_profile out of reange.'),
    ])
    environment = StringField('Environment *', [
        validators.length(min=2, max=250, message='Branch out of reange.'),
        validators.DataRequired(message='Environment requerid.')
    ])


class GcpForm(FlaskForm):
    squad = StringField('Squad', [
        validators.length(min=4, max=50, message='Squad out of reange.'),
        validators.DataRequired(message='Squad Name requerid.')
    ])
    environment = StringField('Environment', [
        validators.length(min=2, max=250, message='Branch out of reange.'),
        validators.DataRequired(message='Environment requerid.')
    ])
    gcloud_keyfile_json = TextAreaField('gcloud keyfile json', [
        validators.DataRequired(message='The gcloud keyfile json is required.')
    ], render_kw={'rows': 20})


class AzureForm(FlaskForm):
    squad = StringField('Squad', [
        validators.length(min=4, max=50, message='Squad out of reange.'),
        validators.DataRequired(message='Squad Name requerid.')
    ])
    environment = StringField('Environment', [
        validators.length(min=2, max=250, message='Branch out of reange.'),
        validators.DataRequired(message='Environment requerid.')
    ])
    subscription_id = StringField('Subscription id', [
        validators.length(
            min=4, max=50, message='Subscription id out of reange.'),
        validators.DataRequired(message='Subscription id requerid.')
    ])
    client_id = StringField('Client id', [
        validators.length(
            min=4, max=50, message='Client_id out of reange.'),
        validators.DataRequired(message='Client_id.')
    ])
    client_secret = StringField('Client secret', [
        validators.length(
            min=4, max=50, message='Client secret out of reange.'),
        validators.DataRequired(message='client_secret.')
    ])
    tenant_id = StringField('tenant_id', [
        validators.length(
            min=4, max=50, message='Tenant id out of reange.'),
        validators.DataRequired(message='tenant_id.')
    ])
