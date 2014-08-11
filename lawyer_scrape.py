import urllib
import time
from bs4 import *
import re
import mechanize
from mechanize import Browser
from socket import error as SocketError

mech = Browser()

mech.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
mech.add_password('https://www.nebraska.gov/', 'USERNAME', 'PASSWORD')
mech.set_handle_robots(False)

baseurl = "https://www.nebraska.gov/justice/name.cgi"

z = open('lawyer_name.txt', 'wb')

firstcounter = 0
while firstcounter < 5:
    try:
        mech.open(baseurl)
        firstcounter = 5
        print "Got nebraska.gov"
    except mechanize.HTTPError, e:
        print "Broke on first loop. I'll try to load the search form again."
        firstcounter += 1
        time.sleep(30)
        print "Taking a 30-second nap."
    except SocketError, e:
        print "Broke on first loop w/ socket error. I'll try to load the search form again."
        firstcounter += 1
        print "Taking a 30-second nap."
        time.sleep(30)
    except:
        print "Uggggghhhhh"
        firstcounter += 1
        time.sleep(45)

formcounter = 0
while formcounter < 5:
    try:
        forms = [f for f in mech.forms()]
        mech.form = forms[0]
        print "found the correct search form"
        mech.form['attorney_name'] = ['ATTORNEY NUMBER GOES HERE']
        formcounter = 5
    except:
        print "are you kidding me"
        formcounter += 1
        time.sleep(30)

print "Form filled out. Submitting."
secondcounter = 0
while secondcounter < 5:
    print "Take %s." % secondcounter
    try: 
        mech.submit()
        print "Got results from filling out the form. Setting counter to five and breaking out of loop."
        secondcounter = 5
    except mechanize.HTTPError, e:
        secondcounter += 1
        print "Broke on first loop, trying to submit filled out search form. Trying again."
        print "taking a 30 second nap"
        time.sleep(30)
    except SocketError, e:
        print "Broke on first loop, socket error, trying to submit search form. Trying again."
        secondcounter += 1
        print "taking a 30 second nap"
        time.sleep(30)
    except:
        print "something is really really really not working here"
        pass

while True:
    soup = BeautifulSoup(mech.response())
    forms = [s for s in mech.forms()]
    table = soup.findAll('table')[0]
    trs = table.findAll('tr')

    for tr in trs:
        tds = tr.findAll('td')
        spans = tds[0].findAll('span')
        client = spans[0].text.strip().replace('\t','')
        print client
        case = spans[2].text.strip()
        judge = spans[3].text.strip().replace("Judge: ","")
        casenum = tds[1].strong.text.strip().replace('\t','').replace('\n','').replace('\r','').replace('Case Number: ','')
        county = tds[1].div.span.text.strip()
        fullrec = (client, case, judge, casenum, county)
        z.write("|".join(fullrec) + "\n")
        time.sleep(1)
    
    if soup.find('button', {'value': 'Next'}):
        for i, form in enumerate(forms):
            for control in form.controls:
                if control.value == "Next":
                    mech.select_form(nr=i)
                    mech.submit()
    else:
        break

z.flush()
z.close()
