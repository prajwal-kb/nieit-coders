from blinker import receiver_connected
from flask import Flask
import smtplib, ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_mysqldb import MySQL

sendEmail = Flask(__name__)
mysql = MySQL(sendEmail)

def sendMail():
	cur = mysql.connection.cursor()
	values = cur.execute("SELECT * FROM user_email ORDER BY id DESC LIMIT 1")
	if values > 0:
		lastRow = cur.fetchone()
	sender_email = os.environ.get('MOVIEDATABASEUSER')
	receiver_email = lastRow['email']
	password = os.environ.get('MOVIEDATABASEPASSWORD')
	user_name = lastRow['username']
	
	message = MIMEMultipart("alternative")
	message["Subject"] = "Welcome to Movie Club :)"
	message["From"] = sender_email
	message["To"] = receiver_email
	cur.close()

	html = """\
	<html>
		<body>
		<p>Hi """ + user_name + """,<br>
			<p> Thank You for signing up for our site. <p>
			<p> Your account in MOVIE CLUB has been created successfully. </p>
			<br><br><br>
			<p> MOVIE CLUB Team. </p>
		
		</p>
		</body>
	</html>
	"""

	# Turn these into plain/html MIMEText objects
	part2 = MIMEText(html, "html")

	# Add HTML/plain-text parts to MIMEMultipart message
	# The email client will try to render the last part first
	message.attach(part2)

	# Create secure connection with server and send email
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
		server.login(sender_email, password)
		server.sendmail(sender_email, receiver_email, message.as_string())