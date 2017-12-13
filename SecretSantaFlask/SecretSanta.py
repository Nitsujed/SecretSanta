import yaml
from flask import Flask, render_template, flash, request, redirect
from wtforms import Form, validators, StringField

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

yml_file = 'wish_list.yml'


class ReusableForm(Form):
    """
    Generate the form fields
    """
    name = StringField('Name:')
    love_this = StringField('Love This:')
    collections = StringField('Collection:')
    hobbies = StringField('Hobbies:')
    favorites = StringField('Favorites:')
    on_list = StringField('On the list:')
    avoid = StringField('Avoid:')
    secret_password = StringField('Secret:', validators=[validators.required(),
                                                         validators.AnyOf('SuperDuperSecretPassword', message='Error')])


def open_db():
    """
    Open the wish list yaml file to track and maintain a database of what the user enters

    Returns:
        wish_lists(dict): dictionary object of the database

    """
    with open(yml_file, 'r') as ymlfile:
        wish_lists = yaml.load(ymlfile)
    return wish_lists


def write_db(wish_lists):
    """
    Writes the wish list dictionary back to the yaml file for storage

    Args:
        wish_lists(dict): Dictionary of the wish list items

    """
    with open(yml_file, 'w') as ymlfile:
        yaml.dump(wish_lists, ymlfile, default_flow_style=False)


@app.route("/santa.html", methods=['GET', 'POST'])
def santa():
    """
    Wish list form website

    """
    wish_lists = open_db()
    form = ReusableForm(request.form)

    print(form.errors)

    if request.method == 'POST':
        name = request.form['name'].lower()
        love_this = request.form['love_this']
        collections = request.form['collections']
        hobbies = request.form['hobbies']
        favorites = request.form['favorites']
        on_list = request.form['on_list']
        avoid = request.form['avoid']
        if love_this != wish_lists[name]['love_this']:
            wish_lists[name]['love_this'] = love_this
        if collections != wish_lists[name]['collections']:
            wish_lists[name]['collections'] = collections
        if hobbies != wish_lists[name]['hobbies']:
            wish_lists[name]['hobbies'] = hobbies
        if favorites != wish_lists[name]['favorites']:
            wish_lists[name]['favorites'] = favorites
        if on_list != wish_lists[name]['on_list']:
            wish_lists[name]['on_list'] = on_list
        if avoid != wish_lists[name]['avoid']:
            wish_lists[name]['avoid'] = avoid
        write_db(wish_lists)
        return redirect('/')

    return render_template('santa.html',
                           form=form)


@app.route('/', methods=['POST', 'GET'])
def index():
    """
    Index website. Requires the user to choose a name from the dropdown and enter in the shared password to proceed to the next page

    Returns:
        index.html if password incorrect, and santa.html if correct

    """
    form = ReusableForm(request.form)

    if request.method == 'POST':
        if form.validate():
            # Save the comment here.
            flash('Thanks for registering ')

        else:
            flash('Good try bub... wrong password ')
            return redirect('/')

        wish_lists = open_db()
        name = request.form['Item_1'].lower()
        print(wish_lists[name]['collections'])
        return render_template('santa.html',
                               form=form,
                               name=name.title(),
                               love_this=wish_lists[name]['love_this'],
                               collections=wish_lists[name]['collections'],
                               hobbies=wish_lists[name]['hobbies'],
                               favorites=wish_lists[name]['favorites'],
                               on_list=wish_lists[name]['on_list'],
                               avoid=wish_lists[name]['avoid'])
    return render_template('index.html', form=form)


if __name__ == "__main__":
    app.run(debug=False)
