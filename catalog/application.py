from flask import Flask, render_template, url_for, request, redirect, flash, \
jsonify, session as login_session, make_response, abort
# from flask_security import login_required
import random, string, httplib2, json, requests, os
from db_setup import Base, User, Item
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

CLIENT_ID = json.loads(open('client_secret.json', 'r').read())\
['web']['client_id']
APPLICATION_NAME = "Item Catalog"

app = Flask(__name__)

engine = create_engine('sqlite:///itemcatalog.db', \
connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Views
@app.route('/')
def main():
    return render_template('base.html') # adjust to add quick info/ direct to login

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        newUser = User(email=request.form['email'], \
        password=request.form['password'])
        session.add(newUser)
        session.commit()

        login_session['email'] = newUser.email
        login_session['password'] = newUser.password
        login_session['logged_in'] = True
        flash('User created successfully')
        return redirect(url_for('catalogHome')) # will contain user_email context
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    login_session.pop('logged_in', None)
    return redirect(url_for('main'))

@app.route('/catalog/')
def catalogHome():
    allItems = session.query(Item).limit(20).all()
    # add categories rep to loop through and show active categories
    # categories = session.query(Item).filter_by(category=category)
    categories = ['home', 'sports', 'clothing', 'business', 'personal']
    return render_template('categories.html', items=allItems, categories=categories)

@app.route('/catalog/<category>/')
@app.route('/catalog/<category>/items/')
def categoryItems(category):
    # this different endpoint necessary? trying to separte logged in views and general view
    itemsByCategory = session.query(Item).filter_by(category=category).all()
    return render_template('categories.html', category=category, \
    items=itemsByCategory)

@app.route('/catalog/<category>/<int:item_id>')
def itemInfo(category, item_id):
    try:
        item = session.query(Item).filter_by(id=item_id).one()
        if item:
            return render_template('show_item.html', category=category, item=item)
    except:
        return 'Item not found', 404

@app.route('/catalog/item/new', methods=['GET', 'POST']) #took out <category> in link/function, categ=categ in if
def newItem():
    if request.method == 'POST':
        itemToAdd = Item(name=request.form['name'], \
        category=request.form['categories'], description=\
        request.form['description'])
        session.add(itemToAdd)
        session.commit()
        flash('Item added')
        # return redirect(url_for('categoryItems', item=itemToAdd, category=itemToAdd.category))
        return redirect(url_for('catalogHome'))
    else:
        return render_template('newitem.html')

# confirm this one below is right, need unique item w/ id to find
@app.route('/catalog/<category>/<int:item_id>/edit', methods=['GET', 'POST'])
# @login_required
def editItem(category, item_id):
    itemToEdit = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            itemToEdit.name = request.form['name']
        if request.form['categories']:
            itemToEdit.category = request.form['categories']
        if request.form['description']:
            itemToEdit.description = request.form['description']
        session.add(itemToEdit)
        session.commit()
        flash('Updated item info')
        return redirect(url_for('categoryItems', category=category))
    else:
        return render_template('edit_item.html', item=itemToEdit, \
        item_id=item_id, category=category)

@app.route('/catalog/<category>/<item_id>/delete', methods=['GET', 'POST'])
# @login_required
def deleteItem(category, item_id):
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item deleted')
        return redirect(url_for('categoryItems', category=category))
    else:
        return render_template('delete_item.html', item=itemToDelete, item_id=item_id, category=category)

@app.route('/catalog.json/')
def jsonCatalog():
    pass
    # items = session.query(Item).all()
    # return jsonify(items)

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(port=8000, debug=True)
