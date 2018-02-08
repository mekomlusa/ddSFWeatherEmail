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
try:
    # Python 3
    import urllib.request as urllib
except ImportError:
    # Python 2
    import urllib2 as urllib

# weather
weather = Weather()

# Lookup via location name.
location = weather.lookup_by_location('San Francisco, CA')
condition = location.condition()
print(condition.text())
forecasts = location.forecast()
l = []
for forecast in forecasts[:3]:
    l.append("Date: "+forecast.date()+"<br>Weather condition: "+forecast.text()+"<br>High: "+
             forecast.high()+"F<br>Low: "+forecast.low()+"F<br>")
body = "Hi DD, \n\nthis is a weather forecast specially prepared for you by @mlusa! Enjoy :)\n\nLocation: San Francisco, CA\n\nCurrent weather condition: "+str(condition.text())+"""\n\nThree days forecast: """+str(l[0])+str(l[1])+str(l[2])+"""Love,\nMlusa\n\n"""+datetime.datetime.today().strftime("%B %d, %Y")

# sendgrid

sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
from_email = Email("noreply@mlusareport.com")
subject = datetime.datetime.today().strftime("%B %d, %Y")+" SF Weather Report"
to_email = Email("Janeddhongchang@gmail.com")
content = Content("text/html","hey")
mail = Mail(from_email, subject, to_email, content)
mail.personalizations[0].add_substitution(Substitution("-user-", "DD"))
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
    exit()
print(response.status_code)
print(response.body)
print(response.headers)
