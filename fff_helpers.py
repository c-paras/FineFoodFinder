from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


def filter_restaurants(restaurants, name="", cuisine="", cost="", suburb="", rating="", any_field=False):
    print(name, cuisine, suburb)
    results = []
    for r in restaurants:
        search_all_fields = [r.get_name(), r.get_cuisine(), r.get_suburb()]
        any_search = False

        if any_field:
            for field in search_all_fields:
                if any_field.lower() in field.lower():
                    any_search = True
                    break
        name_search = name and name.lower() in r.get_name().lower()
        cuisine_search = cuisine and cuisine.lower() in r.get_cuisine().lower()
        # cost_search = search_term <= r.get_cost() <= search_term2
        suburb_search = suburb and suburb.lower() in r.get_suburb().lower()
        # rating_search = search_term <= r.get_rating() <= search_term2

        if any_search or name_search or cuisine_search or suburb_search:  # TODO or suburb_search or rating_search:
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