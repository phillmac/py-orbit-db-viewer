from flask_wtf import FlaskForm
from wtforms import validators, StringField, RadioField, IntegerField, TextAreaField

class RequiredIf(validators.DataRequired):
    # a validator which makes a field required if
    # another field is set and has a truthy value

    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)

class ConnectionForm(FlaskForm):

    orbitdb_addr_prot   = RadioField('OrbitDb API Secure', choices=[('http://', 'http://'), ('https://','https://')], default='https://', validators=[validators.DataRequired()], render_kw={'class':'form-control'})
    orbitdb_host        = StringField('Orbitdb API Address', validators=[validators.DataRequired()], render_kw={'class':'form-control', 'placeholder': 'localhost'})
    orbitdb_port        = IntegerField('OrbitDb API Port', [validators.DataRequired(), validators.NumberRange(1, 65535)], render_kw={'class':'form-control', 'placeholder': '3000'})
    ipfs_host           = StringField('IPFS API Host', [validators.Optional()], render_kw={'class':'form-control', 'placeholder': 'localhost'})
    ipfs_port           = IntegerField('IPFS API Port', [validators.Optional(), validators.NumberRange(1, 65535)], render_kw={'class':'form-control', 'placeholder': '5001'})
    ipfs_addr_prot      = RadioField('IPFS API Secure', choices=[('http://', 'http://'), ('https://','https://')], default='http://', validators=[RequiredIf('ipfs_host')], render_kw={'class':'form-control'})


class DBOpen(FlaskForm):
    database_addr       = StringField('Database Address', [validators.DataRequired()], render_kw={'class':'form-control', 'placeholder': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'})

class DBPut(FlaskForm):
    key = StringField('Key', [validators.DataRequired()], render_kw={'class':'form-control'})
    value = TextAreaField('Value', [validators.DataRequired()], render_kw={'class':'form-control'})

class DBAdd(FlaskForm):
    entry = TextAreaField('Entry', [validators.DataRequired()], render_kw={'class':'form-control'})

class DBQuery(FlaskForm):
    key = StringField('Record Key', [validators.DataRequired()], render_kw={'class':'form-control'})
    comparator = StringField('Comparator', [validators.DataRequired()], render_kw={'class':'form-control'})
    value = StringField('Value', [validators.DataRequired()], render_kw={'class':'form-control'})
