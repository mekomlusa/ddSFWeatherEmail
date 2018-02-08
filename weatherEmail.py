# -*- coding: utf-8 -*-
"""
Created on Tue Feb 06 23:05:00 2018

@author: mlusa
"""

from weather import Weather
import datetime
import sendgrid
import os
from sendgrid.helpers.mail import Email, Content, Substitution, Mail
import psycopg2
import urlparse
try:
    # Python 3
    import urllib.request as urllib
except ImportError:
    # Python 2
    import urllib2 as urllib

# weather
weather = Weather()

# Connect to the database
urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ['DATABASE_URL'])

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

cur = conn.cursor()

# Get all the users here

cur.execute("SELECT * FROM users WHERE push = True;")
try:
# the cat image library should NOT be empty
    recipients = cur.fetchall()
except cur.rowcount == 0:
    raise "No record found in the user table!"

# Lookup via location name.
for r in recipients:
    location = weather.lookup_by_location(r[1])
    condition = location.condition()
    forecasts = location.forecast()
    l = []
    for forecast in forecasts[:3]:
        l.append("Date: "+forecast.date()+"<br>Weather condition: "+forecast.text()+"<br>High: "+
                 forecast.high()+"C<br>Low: "+forecast.low()+"C<br>")
    # sendgrid
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("noreply@mlusareport.com")
    subject = datetime.datetime.today().strftime("%B %d, %Y")+" "+r[1]+" Weather Report"
    to_email = Email(r[3])
    content = Content("text/html","hey")
    mail = Mail(from_email, subject, to_email, content)
    mail.personalizations[0].add_substitution(Substitution("-user-", r[0]))
    mail.personalizations[0].add_substitution(Substitution("-loc-", r[1]))
    mail.personalizations[0].add_substitution(Substitution("-current_weather-", str(condition.text())+"<br>"))
    mail.personalizations[0].add_substitution(Substitution("-day1-", str(l[0])))
    mail.personalizations[0].add_substitution(Substitution("-day2-", str(l[1])))
    mail.personalizations[0].add_substitution(Substitution("-day3-", str(l[2])))
    mail.personalizations[0].add_substitution(Substitution("-today-", datetime.datetime.today().strftime("%B %d, %Y")))
    mail.template_id = "02b2a6ec-926e-4b95-ab7b-70cf93b363ce"
    try:
        response = sg.client.mail.send.post(request_body=mail.get())
    except urllib.HTTPError as e:
        print (e.read())
    print(response.status_code)
    print(response.body)
    print(response.headers)
