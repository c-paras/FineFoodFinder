from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def filter_restaurants(restaurants, name="", cuisine="", cost="", suburb="", rating=""):
    if name:
        restaurants = [r for r in restaurants if name.lower() in r.get_name().lower()]
    if cuisine:
        restaurants = [r for r in restaurants if cuisine.lower() in r.get_cuisine().lower()]
    if suburb:
        restaurants = [r for r in restaurants if suburb.lower() in r.get_suburb().lower()]
    return restaurants


def average(arr):  # Calculates average value of an array
    total = 0
    i = 0
    # Equivalent to for i = 0; i < len(arr); i++
    for i in range(len(arr)): 
        total += arr[i]
    if i == 0:
        return -1
    else:
        return round(total/i, 1)


# Sends an email to the specified address
def send_email(to, body, subject):
    noreply = 'noreply.fine.food.finder@gmail.com'
    noreply_password = '15fac6da-2980-4586-b9f2-ae521261b391'

    # Construct email
    msg = MIMEMultipart()
    msg['From'] = noreply
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send the email from gmail account using smtp
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(noreply, noreply_password)
    server.sendmail(noreply, to, msg.as_string())
    server.quit()