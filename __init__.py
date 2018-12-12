from flask import Flask, render_template, url_for, flash, redirect, request, session, make_response, send_file
from werkzeug.utils import secure_filename
from wtforms import Form, BooleanField, TextField, PasswordField, validators
import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__))) 
from passlib.hash import sha256_crypt
from functools import wraps
from pymysql import escape_string as thwart
import gc

from bs4 import BeautifulSoup
import requests
#from PriceCompare import pricecompare

from db_connect import connection
from app_content import content
from database import database

app = Flask(__name__)

APP_CONTENT = content()
UPLOAD_FOLDER = '/var/www/App400/App400/uploads'
ALLOWED_EXTENSIONS = set(["txt","pdf","png","jpg","jpeg","gif"])

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
 
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash("Please login!")
            return redirect(url_for('login'))
    return wrap  
    
#Upload file checker: "Never Trust User Input"
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    
@app.route("/", methods = ["GET","POST"])
def main():
    try:
        steamtitle = steamtitlecards()
        greenmantitle = pricecomparegreenman()
        c, conn = connection()
        if request.method == "POST":
            entered_username = request.form['username']
            entered_password = request.form['password']
        
            data = c.execute("SELECT * FROM users WHERE username = ('{0}')".format(thwart(request.form['username'])))

            data = c.fetchone()[2]

            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['username'] = request.form['username']
                flash("You are now logged in as "+ session['username']+"!")
                return redirect(url_for("price_compare"))
            else:
                error = "Invalid Credentials. Please Try Again."
                return render_template("login.html", error = error)
        else:
            return render_template("main.html", steamtitle = steamtitle, greenmantitle = greenmantitle)
    except Exception as e:
        return render_template("500.html", error = e)
    
"""
#Output = output because output is in here, but Output is out there
@app.route("/welcome/")
@login_required
def templating():
    try:
        output = ["DIGIT400 is good","Python, Java, php, SQL, C++","<p><strong>Hello world!</strong></p>",42,"42"]
        return render_template("templating_demo.html", output = output)
    except Exception as e:
        return(str(e)) # remove for production
"""

@app.route("/login/", methods=["GET","POST"])
def login():
    error = ""
    try:
        c, conn = connection()
        if request.method == "POST":
            entered_username = request.form['username']
            entered_password = request.form['password']
            
            data = c.execute("SELECT * FROM users WHERE username = ('{0}')".format(thwart(request.form['username'])))
            
            data = c.fetchone()[2]
            
            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['username'] = request.form['username']
                flash("You are now logged in as"+ session['username']+"!")
                return redirect(url_for("price_compare"))
            else:
                error = "Invalid Credentials. Please Try Again."
                return render_template("login.html", error = error)
        else:
            return render_template("login.html")
                
    except Exception as e:
        return render_template("login.html", error = error)
    
@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('main'))

class RegistrationForm(Form):
    username = TextField("Username", [validators.Length(min=4, max=20)])
    email = TextField("Email Address", [validators.Length(min=6, max=50)])
    password = PasswordField("New Password", [validators.Required(),
                                             validators.EqualTo("confirm", message="Entered passwords must match.")])
    confirm = PasswordField("Repeat Password")
    accept_tos = BooleanField("I accept the Terms of Service and Privacy Notice", [validators.Required()])

@app.route('/register/', methods=["GET","POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)
        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            
            c, conn = connection()
            
            x = c.execute("SELECT * FROM users WHERE username=('{0}')".format((thwart(username))))
            
            if int(x) > 0:
                flash("That username is already taken, please choose another.")
                return render_template("register.html", form = form)
            else:
                c.execute("INSERT INTO users(username, password, email, tracking) VALUES ('{0}','{1}','{2}','{3}')".format(thwart(username),thwart(password),thwart(email),thwart("/dashboard/")))
                
            conn.commit()
            flash("Thanks for registering!")
            c.close()
            conn.close()
            gc.collect()
            
            session['logged_in'] = True
            session['username'] = username
            
            return redirect(url_for("dashboard"))
        
        return render_template("register.html", form = form)    
    except Exception as e:
        return(str(e)) #remember to remove, for debugging only
"""    
@app.route("/dashboard/")
def  dashboard():
    try:
        return render_template("dashboard.html", APP_CONTENT = APP_CONTENT)
    except Exception as e:
        return render_template("500.html", error = e)
    
    
@app.route('/uploads/', methods=['GET','POST'])
@login_required
def upload_file():
    try:
        if request.method == 'POST':
            if 'file' not in request.files: #check to see if we have a valid file name with file type suffix
                flash('Incomplete filename. Please add valid file type suffix.')
                return redirect(request.url)
            file = request.files['file'] # if we have a valid file suffix, we'll check to see if it has a filename too.
            if file.filename == '':
                flash("Incomplete filename. Please add valid filename.")
                return redirect(request.url)
            if file and allowed_file(file.filename): # the 2 lines below all that are needed to save images from scraping
                filename = secure_filename(file.filename) 
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                #store username and associated filenames
                database(session["username"],filename)
                flash("File upload successful.")
                return render_template("uploads.html", filename = filename)
            else:
                flash("Invalid file type. Please add valid filename.")
                return redirect(request.url)
        return render_template("uploads.html")
    except Exception as e:
        return(str(e)) # remove for production
    

@app.route("/download/")
@login_required
def download():
    try:
        return send_file('/var/www/App400/App400/uploads/golden.jpg', attachment_filename="Alternative_Facts.jpg")
    except Exception as e:
        return(str(e)) # remove for production

@app.route("/downloader/", methods=["GET","POST"])
@login_required
def downloader():
    error = ''
    try:
        if request.method == "POST":
            filename = request.form['filename']
            return send_file('/var/www/App400/App400/uploads/'+filename, attachment_filename='download')
        return render_template('downloader.html', error = error)
    
    except Exception as e:
        return(str(e)) # remove for production
"""

def steamtitlecards():
    url = 'https://store.steampowered.com/search/?specials=1'
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    
    imgs = str(html.find_all('div', class_='col search_capsule'))
    images = imgs.replace('img','img style="width:12rem;height:6rem;justify-content:center;"')[1:-1].split(", ")
    
    names = str(html.find_all('span', class_='title'))
    titles = names[1:-1].replace('\\xae','&reg;').split(", ")
    
    discounts = str(html.find_all('div', class_='col search_discount responsive_secondrow'))
    discount = discounts.replace('\\n','').replace('span','span style="color: #00AC18;"')[1:-1].split(", ")
    
    newprice = str(html.find_all('div', class_="col search_price discounted responsive_secondrow"))
    price = newprice.replace('\\t','').replace('\\n','').replace('<strike>','<strike style="color: #C2210A;">').replace('<br/>',' ')[1:-1].split(", ")
    
    steamtitles = []
    for a,b,c,d in zip(images, titles, discount, price):
        steamtitles += [a,b,c,d]
        
    steamtitle = [a+b+c+d for a,b,c,d  in zip(steamtitles[0::4], steamtitles[1::4], steamtitles[2::4], steamtitles[3::4])]
    
    return steamtitle

def pricecomparegreenman():
    url = 'https://www.greenmangaming.com/hot-deals/'
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    
    imgs = str(html.find_all('img', class_='img-full'))
    images = imgs.replace('img','img style="width:12rem;height:6rem;"')[1:-1].split(", ")
    
    discounts = str(html.find_all('div', class_='discount'))
    discount = discounts.replace('\\n','').replace('<p>','<p style="color:#00AC18">')[1:-1].split(", ")
    
    previousprice = str(html.find_all('span', class_="prev-price"))
    prevprice = previousprice.replace('\\t','').replace('\\n','').replace('<span class="prev-price">','<strike style="color: #C2210A;">').replace('</span>','</strike> ')[1:-1].split(", ")
    
    newprice = str(html.find_all('span', class_="current-price"))
    price = newprice.replace('\\t','').replace('\\n','')[1:-1].split(", ")
    
    greenmantitles = []
    for a,b,c,d in zip(images, discount, prevprice, price):
        greenmantitles += [a,b,c,d]
        
    greenmantitle = [a+b+c+d for a,b,c,d  in zip(greenmantitles[0::4], greenmantitles[1::4], greenmantitles[2::4], greenmantitles[3::4])]
    
    return greenmantitle


@app.route("/pricecompare/", methods=["GET","POST"])
def price_compare():
    try:
        steamtitle = steamtitlecards()
        greenmantitle = pricecomparegreenman()
        return render_template("pricecompare.html", steamtitle = steamtitle, greenmantitle = greenmantitle)
    except Exception as e:
        return render_template("500.html", error = e)
    
@app.route("/about/")
def about():
    return render_template("about.html")
                
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template("405.html")

@app.errorhandler(500)
def internal_server(e):
    return render_template("500.html", error = e)

if __name__ == "__main__":
    app.run()