from unittest import result
from flask import Flask, render_template , redirect , url_for , request , flash , session
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_login import login_required, logout_user  
from flask_mysqldb import MySQL         #emable Mysql
from werkzeug.security import generate_password_hash , check_password_hash   #importing hash (for security)
from flask_login import login_required,login_user,logout_user,login_manager,LoginManager,current_user
import yaml             #package   
import os
import sendEmail

app = Flask(__name__)
# Bootstrap(app)            #enbaling Bootstrap

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


mail = Mail(app)

@app.route('/',methods = ['GET','POST'])        #home page
def index():
    return render_template('index.html')        


@app.route('/about/')            #about us page
def about():
    return render_template('about.html')


@app.route('/contact/',methods = ['GET','POST'])        #contact us page
def contactus():
    if request.method == "POST" :
        contactDetails = request.form
        username = contactDetails['username']
        cur = mysql.connection.cursor()
        resultValue = cur.execute("SELECT * FROM user WHERE username = %s",([username]) )
        if resultValue == 0 :
            flash('Please register to fill the form','danger')
            return redirect('/contact')
        cur.execute(f"INSERT INTO contactus VALUES('{contactDetails['username']}','{contactDetails['phone_number']}','{contactDetails['email']}','{contactDetails['country']}','{contactDetails['subject']}')")
        mysql.connection.commit()
        cur.close()
        flash('Form submitted successfully!','success')
        return redirect('/')
    return render_template('contact.html')


@app.route('/register/', methods=['GET' , 'POST'])     #signup page
def register():
    if request.method == "POST":
        userDetails = request.form
        username = userDetails['username']
        if userDetails['password'] != userDetails['confirm_password']:
            flash('Passwords do not match! Please Try again', 'danger')
            return render_template('register.html') 
        cur =  mysql.connection.cursor()        #creating cursor
        result = cur.execute("SELECT username FROM user WHERE username = %s",([username]))  
        if result > 0:
            user = cur.fetchone()
            if user['username'] == userDetails['username'] :        #To get a unique user access
                flash('USERNAME already exsist! Please try again', 'danger')
                return render_template('register.html')
        cur.execute(f"INSERT INTO user VALUES('{userDetails['first_name']}','{userDetails['last_name']}','{userDetails['username']}','{userDetails['phone_number']}','{userDetails['email']}','{generate_password_hash(userDetails['password'])}',{userDetails['age']})")     #inserting data into db
        flash('Register successful! Please login.', 'success')
        mysql.connection.commit()
        cur.close()
        sendEmail.sendMail()
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
                flash('Please enter the correct password', 'danger')
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
        cur.execute(f"INSERT INTO theatre(theatreid,theatrename,t_ph_number,t_email,location,no_of_seats) VALUES ('{theatreDetails['theatreid']}','{theatreDetails['theatrename']}','{theatreDetails['t_ph_number']}','{theatreDetails['t_email']}','{theatreDetails['location']}','{theatreDetails['no_of_seats']}')")
        mysql.connection.commit()
        cur.close()
        flash('Register successful! Please wait for the comformation mail.', 'success')
        return redirect('/')
    return render_template('theatreregis.html')


@app.route('/theatrelogin/',methods=['GET','POST'])        #theatrelogin page
def theatrelogin():
    if request.method == "POST" :
        theatreDetails = request.form
        theatreid = theatreDetails['theatreid']
        cur = mysql.connection.cursor()
        value = cur.execute("SELECT * FROM theatre WHERE theatreid = %s ",([theatreid]))
        if value > 0:
            theatre = cur.fetchone()
            if theatre['t_password'] == theatreDetails['t_password']:
                session['login'] = True
                session['theatreid'] = theatre['theatreid']
                flash('WELCOME '+ str(session['theatreid']) + '! You have been successfully logged in', 'success')
            else : 
                cur.close()
                flash('Password does not match', 'danger')
                return render_template('theatrelogin.html')
        else:
            cur.close()
            flash('Theatre NOT found', 'danger')
            return render_template('theatrelogin.html')
        cur.close()
        return redirect('/addmovie')
    return render_template('theatrelogin.html')


@app.route('/adminlogin/',methods=['GET','POST'])        #adminlogin page
def adminlogin():
    if request.method == "POST":
        adminDetails = request.form
        adminid = adminDetails['adminid']
        cur = mysql.connection.cursor()
        value = cur.execute("SELECT * FROM admin WHERE adminid = %s",([adminid]))
        if value > 0:
            admin = cur.fetchone()
            if admin['a_password'] == adminDetails['a_password']:
                session['login'] = True
                session['adminid'] = admin['adminid']
                flash('WELCOME '+ str(session['adminid']) + '! You have been successfully logged in', 'success')
            else : 
                cur.close()
                flash('Password does not match', 'danger')
                return render_template('adminlogin.html')
        else:
            cur.close()
            flash('Admin NOT found', 'danger')
            return render_template('adminlogin.html')
        cur.close()
        return redirect('/addtheatre')
    return render_template('adminlogin.html')


@app.route('/addtheatre/',methods = ['GET','POST'])     
def addtheatre():
    if request.method == "POST":
        passwords = request.form.get('t_password')
        theatreid = request.form.get('theatreid')
        theatrename = request.form.get('theatrename')
        cur = mysql.connection.cursor()
        cur.execute("UPDATE theatre SET t_password = %s WHERE theatreid = %s",([passwords],[theatreid]))
        mysql.connection.commit()
        cur.close()
        flash('Password is given to the theatre '+ str(theatrename),'success')
    return render_template('addtheatre.html')


@app.route('/addmovie/',methods = ['GET','POST'])
def addmovie() :
    if request.method == "POST" :
        movieDetails = request.form
        movieid = movieDetails['movie_id']
        cur = mysql.connection.cursor()
        value = cur.execute("SELECT * FROM movie WHERE movie_id = %s",([movieid]))
        if value > 0 :
            flash('Movie is already inserted','warning')
            return redirect('/addmovie')
        cur.execute(f"INSERT INTO movie VALUES('{movieDetails['movie_id']}','{movieDetails['theatreid']}','{movieDetails['m_name']}','{movieDetails['m_director']}','{movieDetails['release_date']}','{movieDetails['language']}')")
        mysql.connection.commit()
        cur.close()
        flash('Movie added successfully','success')
        return redirect('/')
    return render_template('addmovie.html')


@app.route('/book/',methods = ['GET','POST'])
def book():
    if request.method == "POST":
        seatDetails = request.form
        seatno = seatDetails['seatrow'] + seatDetails['seatcol']
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT seatno FROM seat WHERE seatno = %s",([seatno]))  
        if result > 0 :
            seat = cur.fetchone()
            if seat['seatno'] == seatno :        
                flash('This seat is already booked!', 'danger')
                return render_template('book.html')
        cur.execute(f"INSERT INTO seat VALUES('{seatDetails['theatreid']}','{seatDetails['movie_id']}','{seatDetails['m_name']}','{seatno}')")
        mysql.connection.commit()
        cur.close()
        flash ('Successfully booked your ticket. Seat no. '+str(seatno),'success')
        return redirect('/')
    return render_template('book.html')


@app.errorhandler(404)      #error page-> 404
def page_not_found(e) :
    return 'This page was not found'


if __name__ == '__main__':
    app.run(debug=True)