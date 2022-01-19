from flask import Flask, render_template , redirect, url_for , request ,flash
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL  #emable Mysql
import yaml     #package 

app = Flask(__name__)
Bootstrap(app)               #enbaling Bootstrap

#configure db
with open('db.yaml','r') as a :    #opening yaml file
    db = yaml.safe_load(a)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
mysql = MySQL(app)


@app.route('/',methods = ['GET','POST'])
def index():
    # cur =  mysql.connection.cursor()        #creating cursor
    # # cur.execute("INSERT INTO admin VALUES(%s,%s,%s)",[1002,"ajay","ajay007"])     #inserting data into db
    # # mysql.connection.commit()       #save the db
    # result_value = cur.execute("SELECT * FROM admin")
    # if result_value > 0 :
    #     admins = cur.fetchall()
    #     return admins[1]
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e) :
    return 'This page was not found'

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/css')
def css():
    return render_template('css.html')



if __name__ == '__main__':
    app.run(debug=True)
    
