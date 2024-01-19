# -*- encoding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import (BooleanField, PasswordField, StringField, TextAreaField, SelectField,
                     FormField, FieldList, validators)
from wtforms.fields import EmailField
from wtforms.validators import DataRequired


class DictField(StringField):
    def process_formdata(self, valuelist):
        if valuelist:
            data = valuelist[0]
            try:
                # Try to parse the input as a dictionary
                self.data = dict(eval(data))
            except (SyntaxError, ValueError):
                self.data = None
                raise ValueError("Invalid dictionary format")


class ExtraVariableForm(FlaskForm):
    key = StringField('Key')
    value = StringField('Value')


class StackForm(FlaskForm):

    name = StringField(
        "Name",
        [
            validators.length(min=4, max=30, message="Name out of reange."),
            validators.DataRequired(message="Name requerid."),
            validators.Regexp('[\r\n\t\f\v  ]', message="Username must contain only letters numbers or underscore"),
        ],
    )
    git = StringField(
        "Git",
        [
            validators.length(min=4, max=250, message="Git out of reange."),
            validators.DataRequired(message="Git requerid."),
        ],
    )
    branch = StringField(
        "Branch",
        [
            validators.length(min=2, max=30, message="Branch out of reange."),
            validators.DataRequired(message="Branch requerid."),
        ],
    )
    squad_access = TextAreaField(
        "Squad Access (* share with everyone or pass a list: squad1, squad2)",
        default="*",
        render_kw={"rows": 1},
    )
    iac_type = SelectField(
        "IaC Type",
        choices=[('', 'Select an IaC Type'), ('terraform', 'Terraform'), ('tofu', 'openTofu'), ('terragrunt', 'TerraGrunt')],
        validators=[validators.DataRequired()],
        coerce=lambda x: 'tofu' if x == 'openTofu' else x
    )
    tf_version = SelectField(
        "IaC Version",
        validators=[validators.DataRequired(message="IaC version required.")]
    )

    project_path = StringField(
        "Project_path",
        [
            validators.length(min=1, max=500, message="Folder path when use monorepo"),
        ],
    )
    description = StringField(
        "Description",
        [
            validators.length(min=30, max=60, message="Set short Description"),
        ],
    )
    squad_access_edit = StringField(
        "Squad Access (* share with everyone or pass a list: squad1, squad2)",
        render_kw={"rows": 1},
    )

    icon_selector = SelectField('Icon Selector', choices=[], validators=[DataRequired()])


class DeployForm(FlaskForm):
    deploy_name = StringField(
        "Deploy Name",
        [
            validators.length(min=4, max=30, message="Name out of reange."),
            validators.DataRequired(message="Name requerid."),
        ],
    )
    squad = StringField(
        "Squad",
        [
            validators.length(min=4, max=50, message="Squad out of reange."),
            validators.DataRequired(message="Squad requerid."),
        ],
    )
    stack_name = StringField(
        "Stack Name",
        [
            validators.length(min=4, max=50, message="stack out of reange."),
            validators.DataRequired(message="Stack requerid."),
        ],
    )
    environment = StringField(
        "Environment",
        [
            validators.length(min=2, max=25, message="Branch out of reange."),
            validators.DataRequired(message="Environment requerid."),
        ],
    )
    start_time = StringField(
        "Apply Time",
        [
            validators.length(min=3, max=30, message="Time out of reange."),
        ],
    )
    destroy_time = StringField(
        "Destroy Time",
        [
            validators.length(min=3, max=30, message="Time out of reange."),
        ],
    )
    branch = StringField(
        "branch",
        [
            validators.length(
                min=2, max=30, message="Custom branch if empty use stack default branch"
            ),
        ],
    )
    tfvar_file = StringField(
        "tfvar_file",
        [
            validators.length(min=2, max=30, message="Tfvars file name."),
        ],
    )
    project_path = StringField(
        "project_path",
        [
            validators.length(min=2, max=500, message="Project path name."),
        ],
    )
    environment = StringField(
        "Environment",
        [
            validators.length(min=2, max=250, message="Branch out of reange."),
            validators.DataRequired(message="Environment requerid."),
        ],
    )
    variables = TextAreaField("Variables", render_kw={"rows": 5})


class UserForm(FlaskForm):
    role = ["yoda", "darth_vader", "stormtrooper", "R2-D2", "grogu"]
    username = StringField(
        "Username",
        [
            validators.length(min=4, max=20),
        ],
    )
    fullname = StringField(
        "Fullname",
        [
            validators.length(min=4, max=50),
        ],
    )
    email = EmailField(
        "Email",
        [
            validators.length(min=6, max=50),
            validators.DataRequired(message="The email is required."),
            validators.Email(message="Enter a valid email."),
        ],
    )
    squad = StringField(
        "Squad",
        [
            validators.length(min=1, max=50),
            validators.DataRequired("The squad name is required."),
        ],
    )
    password = PasswordField(
        "Password",
        [
            validators.length(min=8, max=50),
            validators.DataRequired("The password is required."),
            validators.EqualTo(
                "confirm_password", message="The password does not match."
            ),
        ],
    )
    confirm_password = PasswordField("Confirm password")
    privilege = BooleanField("", [])
    master = BooleanField("", [])
    is_active = BooleanField("", [])


class AwsForm(FlaskForm):
    squad = StringField(
        "Squad *",
        [
            validators.length(min=4, max=50, message="Squad out of reange."),
            validators.DataRequired(message="Squad Name requerid."),
        ],
    )
    environment = StringField(
        "Environment *",
        [
            validators.length(min=2, max=250, message="Environment out of reange."),
            validators.DataRequired(message="Environment requerid."),
        ],
    )
    access_key_id = StringField(
        "Access_key_id *",
        [
            validators.length(min=4, max=50, message="Access key id out of reange."),
            validators.DataRequired(message="Access_key_id requerid."),
        ],
    )
    secret_access_key = StringField(
        "Secret_access_key *",
        [
            validators.length(
                min=4, max=50, message="Secret Access Key out of reange."
            ),
            validators.DataRequired(message="Secret_access_key."),
        ],
    )
    default_region = StringField(
        "Default_region *",
        [
            validators.length(min=4, max=50, message="Default Region out of reange."),
            validators.DataRequired(message="default_region."),
        ],
    )
    role_arn = StringField(
        "Role_arn",
        [
            validators.length(min=4, max=300, message="Role arn out of reange."),
        ],
    )
    extra_variables = FieldList(FormField(ExtraVariableForm), label='Extra Variables')


class GcpForm(FlaskForm):
    squad = StringField(
        "Squad",
        [
            validators.length(min=4, max=50, message="Squad out of reange."),
            validators.DataRequired(message="Squad Name requerid."),
        ],
    )
    environment = StringField(
        "Environment",
        [
            validators.length(min=2, max=250, message="Branch out of reange."),
            validators.DataRequired(message="Environment requerid."),
        ],
    )
    gcloud_keyfile_json = TextAreaField(
        "gcloud keyfile json *",
        [validators.DataRequired(message="The gcloud keyfile json is required.")],
        render_kw={"rows": 20},
    )


class GcpFormUpdate(FlaskForm):
    squad = StringField(
        "Squad",
        [
            validators.length(min=4, max=50, message="Squad out of reange."),
            validators.DataRequired(message="Squad Name requerid."),
        ],
    )
    environment = StringField(
        "Environment",
        [
            validators.length(min=2, max=250, message="Branch out of reange."),
            validators.DataRequired(message="Environment requerid."),
        ],
    )
    gcloud_keyfile_json = TextAreaField(
        "gcloud keyfile json",
        render_kw={"rows": 20},
    )


class AzureForm(FlaskForm):
    squad = StringField(
        "Squad",
        [
            validators.length(min=4, max=50, message="Squad out of reange."),
            validators.DataRequired(message="Squad Name requerid."),
        ],
    )
    environment = StringField(
        "Environment",
        [
            validators.length(min=2, max=250, message="Branch out of reange."),
            validators.DataRequired(message="Environment requerid."),
        ],
    )
    subscription_id = StringField(
        "Subscription id",
        [
            validators.length(min=4, max=50, message="Subscription id out of reange."),
            validators.DataRequired(message="Subscription id requerid."),
        ],
    )
    client_id = StringField(
        "Client id",
        [
            validators.length(min=4, max=50, message="Client_id out of reange."),
            validators.DataRequired(message="Client_id."),
        ],
    )
    client_secret = StringField(
        "Client secret",
        [
            validators.length(min=4, max=50, message="Client secret out of reange."),
            validators.DataRequired(message="client_secret."),
        ],
    )
    tenant_id = StringField(
        "tenant_id",
        [
            validators.length(min=4, max=50, message="Tenant id out of reange."),
            validators.DataRequired(message="tenant_id."),
        ],
    )


class AzureFormUpdate(FlaskForm):
    squad = StringField(
        "Squad",
        [
            validators.length(min=4, max=50, message="Squad out of reange."),
        ],
    )
    environment = StringField(
        "Environment",
        [
            validators.length(min=2, max=250, message="Branch out of reange."),
        ],
    )
    subscription_id = StringField(
        "Subscription id",
        [
            validators.length(min=4, max=50, message="Subscription id out of reange."),
        ],
    )
    client_id = StringField(
        "Client id",
        [
            validators.length(min=4, max=50, message="Client_id out of reange."),
        ],
    )
    client_secret = StringField(
        "Client secret",
        [
            validators.length(min=4, max=50, message="Client secret out of reange."),
        ],
    )
    tenant_id = StringField(
        "tenant_id",
        [
            validators.length(min=4, max=50, message="Tenant id out of reange."),
        ],
    )


class CustomProviderForm(FlaskForm):
    squad = StringField(
        "Squad",
        [
            validators.length(min=4, max=50, message="Squad out of reange."),
            validators.DataRequired(message="Squad Name requerid."),
        ],
    )
    environment = StringField(
        "Environment",
        [
            validators.length(min=2, max=250, message="Branch out of reange."),
            validators.DataRequired(message="Environment requerid."),
        ],
    )
    configuration = TextAreaField(
        "Configuration",
        [validators.DataRequired(message="Configuration file json is required.")],
        render_kw={"rows": 20},
    )
