import os
import sys
import json
import logging
from functools import wraps
from orbitdbviewer import forms
from orbitdbapi import OrbitDbAPI as OrbitDBClient
from ipfsapi.client import Client as IPFSClient

#from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap
from flask import Flask, render_template, session, redirect, url_for, request, flash

logfmt = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=logfmt, stream=sys.stdout, level=logging.DEBUG)


app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = False
app.secret_key = os.urandom(24)
#csrf = CSRFProtect(app)
bootstrap = Bootstrap(app)

@app.route("/", methods=['POST','GET'])
def index():
    if 'orbitdb_addr' in session:
        return redirect(url_for('database'))
    form = forms.ConnectionForm(request.form)
    if form.validate_on_submit():
        orbitdb_addr = '{}{}:{}'.format(form.orbitdb_addr_prot.data, form.orbitdb_host.data, form.orbitdb_port.data)
        session['orbitdb_addr'] = '{}{}:{}'.format(form.orbitdb_addr_prot.data, form.orbitdb_host.data, form.orbitdb_port.data)
        logging.debug(orbitdb_addr)
        if form.ipfs_host.data and form.ipfs_port.data:
            session['ipfs_host'] = form.ipfs_addr_prot + form.ipfs_host.data
            session['ipfs_port'] = form.ipfs_port.data
        return redirect(url_for('database'))
    else:
        flash_errors(form)
    return render_template('index.html', form=form)

@app.route('/database', methods=['POST','GET'])
def database():
    dbopen = None
    db = None
    dball = None
    database_addr = None
    if not  'orbitdb_addr' in session:
        return redirect(url_for('index'))
    if 'ipfs_addr' in session:
        ipfs = IPFSClient()
        session.get('ipfs_addr')
    dbopen = forms.DBOpen(request.form)
    if dbopen.validate_on_submit() or 'database_addr' in session:
        if dbopen.database_addr.data:
            database_addr = session['database_addr'] = dbopen.database_addr.data
        else:
            database_addr = session['database_addr']
        try:
            db = OrbitDBClient(base_url=session.get('orbitdb_addr')).db('/orbitdb/' + database_addr)
            if db.iterable:
                contents = db.iterator_raw(limit=-1)
                dball = {}
                for item in contents:
                    dball[item.get('hash')] = [*item.get('payload', {}).get('value', {})][0]
                print(dball)
            else:
                dball = db.all()
        except:
            flash('Error connecting to OrbitDB API')
            logging.exception('Failed to connect to OrbitDB API')
            del session['database_addr']
            return redirect(url_for('index'))
    else:
        flash_errors(dbopen)

    return render_template('database.html', db=db, dball=dball,
        dbopen=dbopen,
        dbput=forms.DBPut(),
        dbadd = forms.DBAdd(),
        dbquery=forms.DBQuery()
    )

def validate_db(func):
    @wraps(func)
    def do_validate(*args, **kwargs):
        if not 'orbitdb_addr' in session:
            return redirect(url_for('index'))
        if not 'database_addr' in session:
            return redirect(url_for('database'))
        return func(*args, **kwargs)
    return do_validate


@app.route('/dbput', methods=['POST'])
@validate_db
def dbput():
    dbput = forms.DBPut(request.form)
    if dbput.validate_on_submit():
        try:
            db = OrbitDBClient(base_url=session.get('orbitdb_addr')).db('/orbitdb/' + session.get('database_addr'))
            if db.indexed:
                db.put({db.index_by:dbput.key.data}.update(dbput.value.data))
            else:
                logging.debug('putting {}'.format({'key':dbput.key.data, 'value':dbput.value.data}))
                db.put({'key':dbput.key.data, 'value':dbput.value.data})
        except:
            flash('Error puting to db')
            logging.exception('Failed to put to DB')
    else:
        flash_errors(dbput)
    return redirect(url_for('database'))

@app.route('/dbadd', methods=['POST'])
@validate_db
def dbadd():
    dbadd = forms.DBAdd(request.form)
    if dbadd.validate_on_submit():
        try:
            db = OrbitDBClient(base_url=session.get('orbitdb_addr')).db('/orbitdb/' + session.get('database_addr'))
            db.add(dbadd.entry.data)
        except:
            flash('Error adding to db')
            logging.exception('Failed to add to DB')
    else:
        flash_errors(dbput)
    return redirect(url_for('database'))

@app.route('/dbrm/<item>', methods=['POST'])
@validate_db
def dbrm(item):
    try:
        db = OrbitDBClient(base_url=session.get('orbitdb_addr')).db('/orbitdb/' + session.get('database_addr'))
        db.remove(item)
    except:
        flash('Error removing from db')
        logging.exception('Failed to remove from DB')
    return redirect(url_for('database'))


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash('Error in the {} field - {}'.format(
                getattr(form, field).label.text,
                error
            ))



def to_pretty_json(value):
    return json.dumps(value, sort_keys=True,
                      indent=4, separators=(',', ': '))

app.jinja_env.filters['tojson_pretty'] = to_pretty_json

if __name__ == '__main__':
    app.run(debug=True)