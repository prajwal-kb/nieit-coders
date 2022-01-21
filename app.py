import re
from flask import Flask, render_template , redirect , url_for , request , flash , session
from flask_bootstrap import Bootstrap           #importing the bootstrap
from flask_mysqldb import MySQL         #emable Mysql
from werkzeug.security import generate_password_hash , check_password_hash   #importing hash (for security)
from flask_login import login_required,login_user,logout_user,login_manager,LoginManager,current_user
import yaml             #package   
import os

app = Flask(__name__)
Bootstrap(app)            #enbaling Bootstrap

#configure db
with open('db.yaml','r') as a :    #opening yaml file
    db = yaml.safe_load(a)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


app.config['SECRET_KEY'] = os.urandom(24)       #generate random string

#getting the unique user access
# login_manager = LoginManager(app)
# login_manager.login_view = 'Login'

# @login_manager.user_loader
# def load_user(username) :
#     return username.query.get(username)

@app.route('/',methods = ['GET','POST'])        #home page
def index():
    return render_template('index.html')        


@app.route('/about/')            #about us page
def about():
    return render_template('about.html')


@app.route('/contact/')          #contact us page
def css():
    return render_template('contact.html')


@app.route('/register/', methods=['GET' , 'POST'])     #signup page
def register():
    if request.method == "POST":
        userDetails = request.form
        if userDetails['password'] != userDetails['confirm_password']:
            flash('Passwords do not match! Plese Try again.', 'danger')
            return render_template('register.html')
        cur =  mysql.connection.cursor()        #creating cursor 
        cur.execute(f"INSERT INTO user VALUES('{userDetails['first_name']}','{userDetails['last_name']}','{userDetails['username']}','{userDetails['phone_number']}','{userDetails['email']}','{generate_password_hash(userDetails['password'])}',{userDetails['age']})")     #inserting data into db
        mysql.connection.commit()
        cur.close()
        flash('Register successful! Please login.', 'success')
        return redirect('/login')
    return render_template('register.html')


@app.route('/login/',methods=['GET','POST'])        #login page
def login():
    if request.method == "POST":
        userDetails = request.form
        username = userDetails['username']
        cur =  mysql.connection.cursor()
        resultValue = cur.execute("SELECT * FROM user WHERE username = %s",([username]) )
        if resultValue > 0 :
            user = cur.fetchone()
            if check_password_hash(user['password'], userDetails['password']):
                session['login'] = True
                session['first_name'] = user['first_name']
                session['last_name'] = user['last_name']
                flash('WELCOME '+ session['first_name'] +'! You have been successfully logged in', 'success')
            else:
                cur.close()
                flash('Password does not match', 'danger')
                return render_template('login.html')
        else:
            cur.close()
            flash('User not found', 'danger')
            return render_template('login.html')
        cur.close()
        return redirect('/')
    return render_template('login.html')

@app.route('/theatreregis/',methods=['GET','POST'])        #theatrelogin page
def theatreregis():
    if request.method == "POST" :
        theatreDetails = request.form
        cur = mysql.connection.cursor()
        cur.execute(f"INSERT INTO theatre VALUES ('{theatreDetails['theatreid']}','{theatreDetails['theatrename']}','{theatreDetails['t_ph_number']}','{theatreDetails['t_email']}')")
        mysql.connection.commit()
        cur.close()
        flash('Register successful! Please wait for the comformation mail.', 'success')
        return redirect('/')
    return render_template('theatreregis.html')


@app.route('/theatrelogin/',methods=['GET','POST'])        #theatrelogin page
def theatrelogin():
    return render_template('theatrelogin.html')


@app.route('/adminlogin/',methods=['GET','POST'])        #adminlogin page
def adminlogin():
    if request.method == "POST":
        adminDetails = request.form
        adminid = adminDetails['adminid']
        cur = mysql.connection.cursor()
        
    return render_template('adminlogin.html')


@app.route('/logout/',methods=['GET','POST'])        #logout page -> home page
def logout():
    return render_template('logout.html')



@app.errorhandler(404)      #error page-> 404
def page_not_found(e) :
    return 'This page was not found'


if __name__ == '__main__':
    app.run(debug=True)