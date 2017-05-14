from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


def filter_restaurants(restaurants, name="", cuisine="", max_cost="", suburb="", rating="", any_field=""):
    results = []
    for r in restaurants:
        # TODO suburb_search and rating_search:
        satisfies = True
        if name:
            satisfies = satisfies and name.lower() in r.get_name().lower()
        if cuisine:
            satisfies = satisfies and cuisine.lower() in r.get_cuisine().lower()
        if suburb:
            satisfies = satisfies and suburb.lower() in r.get_suburb().lower()
        if max_cost:
            satisfies = satisfies and int(max_cost) > r.get_cost()

        if any_field:
            search_all_fields = [r.get_name(), r.get_cuisine(), r.get_suburb()]
            any_search = False
            for field in search_all_fields:
                if any_field.lower() in field.lower():
                    any_search = True
                    break
            satisfies = satisfies and any_search

        if satisfies:
            results.append(r)
    return results


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