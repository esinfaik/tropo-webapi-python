#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from django.utils import simplejson
import cgi
import logging
import tropo_web_api
import GoogleS3
from xml.dom import minidom
from google.appengine.api import urlfetch
from xml.etree import ElementTree

AWS_ACCESS_KEY_ID = 'xxxxx'
AWS_SECRET_ACCESS_KEY = 'xxxxx'
S3_BUCKET_NAME = "xxxxxx"
YOUR_PHONE_NUMBER = "tel:+1xxxxxxxxxx"
THIS_URL = "http://xxxxxx"

AMAZON_S3_URL = "http://s3.amazonaws.com"
GOOGLE_WEATHER_API_URL = "http://www.google.com/ig/api"


def HelloWorld(handler, tropo):
    """
    This is the traditional "Hello, World" function. The idiom is used throughout the API. We consturct a Tropo object, and then flesh out that object by calling "action" functions (in this case, tropo.say). Then call tropo.Render, which translates the Tropo object into JSON format. Finally, we write the JSON object to the standard output, so that it will get POSTed back to the API.
    """
    tropo.say ("Hello, World")
    json = tropo.RenderJson()
    logging.info ("HelloWorld json: %s" % json)
    handler.response.out.write(json)

def WeatherDemo(handler, tropo):
    """
    """
    choices = tropo_web_api.Choices("[5 digits]").obj

    tropo.ask(choices, 
              say="Please enter your 5 digit zip code.", 
              attempts=3, bargein=True, name="zip", timeout=5, voice="dave");

    tropo.on(event="continue", 
             next="%s/weather.py?uri=end" % THIS_URL,
             say="Please hold.")

    tropo.on(event="error",
             next="%s/weather.py?uri=error" % THIS_URL,
             say="Ann error occurred.")

    json = tropo.RenderJson()
    logging.info ("Json result: %s " % json)
    pretty = tropo.PrettyJson()
    logging.info ("WeatherDemo json: %s" % pretty)

    handler.response.out.write(pretty)

def RecordDemo(handler, tropo):

    url = "%s/receive_recording.py" % THIS_URL
    choices_obj = tropo_web_api.Choices("", terminator="#").json
    tropo.record(say="Tell us about yourself", url=url, 
                 choices=choices_obj)
    json = tropo.RenderJson()
    logging.info ("Json result: %s " % json)
    handler.response.out.write(json)

def SMSDemo(handler, tropo):

    tropo.message("Hello World", YOUR_PHONE_NUMBER, channel='TEXT', network='SMS', timeout=5)
    json = tropo.RenderJson()
    logging.info ("Json result: %s " % json)
    handler.response.out.write(json)


def RecordHelloWorld(handler, tropo):
    """
    This is the traditional "Hello, World" function. The idiom is used throughout the API. We construct a Tropo object, and then flesh out that object by calling "action" functions (in this case, tropo.say). Then call tropo.Render, which translates the Tropo object into JSON format. Finally, we write the JSON object to the standard output, so that it will get POSTed back to the API.
    """
    # http://www.s3fm.com/
    url = "/receive_recording.py"
    tropo.startRecording(url)
    tropo.say ("Hello, World.")
    tropo.stopRecording()
    json = tropo.RenderJson()
    logging.info ("RecordHelloWorld json: %s" % json)
    handler.response.out.write(json)

def RedirectDemo(handler, tropo):
    """
    This is the traditional "Hello, World" function. The idiom is used throughout the API. We construct a Tropo object, and then flesh out that object by calling "action" functions (in this case, tropo.say). Then call tropo.Render, which translates the Tropo object into JSON format. Finally, we write the JSON object to the standard output, so that it will get POSTed back to the API.
    """
    tropo.say ("One moment please.")
    tropo.redirect(MY_PHONE)
    json = tropo.RenderJson()
    logging.info ("RecordHelloWorld json: %s" % json)
    handler.response.out.write(json)

def TransferDemo(handler, tropo):
    """
    This is the traditional "Hello, World" function. The idiom is used throughout the API. We construct a Tropo object, and then flesh out that object by calling "action" functions (in this case, tropo.say). Then call tropo.Render, which translates the Tropo object into JSON format. Finally, we write the JSON object to the standard output, so that it will get POSTed back to the API.
    """
    # http://www.s3fm.com/
    tropo.say ("One moment please.")
    tropo.transfer(MY_PHONE)
    tropo.say("Hi. I am a robot")
    json = tropo.RenderJson()
    logging.info ("RecordHelloWorld json: %s" % json)
    handler.response.out.write(json)



DEMOS = {
 '1' : ('Hello World', HelloWorld),
 '2' : ('Weather Demo', WeatherDemo),
 '3' : ('Record Demo', RecordDemo),
 '4' : ('SMS Demo', SMSDemo),
 '5' : ('Record Conversation Demo', RecordHelloWorld),
 '6' : ('Redirect Demo', RedirectDemo),
 '7' : ('Transfer Demo', TransferDemo),
}

class TropoDemo(webapp.RequestHandler):
    """
    This class is the entry point to the Tropo Web API for Python demos. Note that it's only method is a POST method, since this is how Tropo kicks off.
        
    A bundle of information about the call, such as who is calling, is passed in via the POST data.
    """
    def post(self):
        if (1):
            tropo = tropo_web_api.Tropo()
            tropo.say ("Welcome to the Tropo web API demo")

            request = "Please press"
            choices_string = ""
            choices_counter = 1
            for key in sorted(DEMOS.iterkeys()):
                if (len(choices_string) > 0):
                    choices_string = "%s,%s" % (choices_string, choices_counter)
                else:
                    choices_string = "%s" % (choices_counter)
                demo_name = DEMOS[key][0]
                demo = DEMOS[key][1]
                request = "%s %s for %s," % (request, key, demo_name)
                choices_counter += 1
            choices = tropo_web_api.Choices(choices_string).obj

            tropo.ask(choices, say=request, attempts=3, bargein=True, name="zip", timeout=5, voice="dave")

            tropo.on(event="continue", 
                     next="%s/demo_continue.py" % THIS_URL,
                     say="Please hold.")

            tropo.on(event="error",
                     next="%s/demo_continue.py" % THIS_URL,
                     say="An error occurred.")

            json = tropo.RenderJson()
            logging.info ("Json result: %s " % json)
            self.response.out.write(json)


class TropoDemoContinue(webapp.RequestHandler):
    """
    This class implements all the top-level demo functions. Data is POSTed to the application, to start tings off. After retrieving the result value, which is a digit indicating the user's choice of demo function, the POST method dispatches to the chosen demo.
    """
    def post (self):
        json = self.request.body
        logging.info ("json: %s" % json)
        tropo = tropo_web_api.Tropo()
        result = tropo_web_api.Result(json)
        choice = result.getValue()
        logging.info ("Choice of demo is: %s" % choice)

        for key in DEMOS:
            
                if (choice == key):
                    demo_name = DEMOS[key][0]
                    demo = DEMOS[key][1]
                    demo(self, tropo)
                    break
    


class Weather(webapp.RequestHandler):
    def post (self):
        json = self.request.body
        logging.info ("json: %s" % json)
        tropo = tropo_web_api.Tropo()
        result = tropo_web_api.Result(json);
        zip = result.getValue()
        google_weather_url = "%s?weather=%s&hl=en" % (GOOGLE_WEATHER_API_URL, zip)
        resp = urlfetch.fetch(google_weather_url)

        logging.info ("weather url: %s " % google_weather_url)
        if (resp.status_code == 200):
            xml = resp.content
            logging.info ("weather xml: %s " % xml)
            doc = ElementTree.fromstring(xml)            
            logging.info ("doc: %s " % doc)
            condition = doc.find("weather/current_conditions/condition").attrib['data']
            temp_f  = doc.find("weather/current_conditions/temp_f").attrib['data']
            wind_condition = doc.find("weather/current_conditions/wind_condition").attrib['data']
            city = doc.find("weather/forecast_information/city").attrib['data']
            logging.info ("condition: %s temp_f: %s wind_condition: %s city: %s" % (condition, temp_f, wind_condition, city))
            tropo = tropo_web_api.Tropo()
            # condition: Partly Cloudy temp_f: 73 wind_condition: Wind: NW at 10 mph city: Portsmouth, NH
            temp = "%s degrees" % temp_f
            wind = self.english_expand (wind_condition)
            tropo.say("Current city is %s . Weather conditions are %s. Temperature is %s. Winds are %s ." % (city, condition, temp, wind))        
            json = tropo.RenderJson()

            self.response.out.write(json)


    def english_expand(self, expr):
        result = expr.replace("NW", "North West")
        result = expr.replace("NE", "North East")
        result = expr.replace("N", "North")
        result = expr.replace("SW", "South West")
        result = expr.replace("SE", "South East")
        result = expr.replace("S", "South")
        result = expr.replace("mph", "miles per hour")
        return result


class ReceiveRecording(webapp.RequestHandler):
    def post(self):
        logging.info ("I just received a post recording")
#        wav = self.request.body
        wav = self.request.get ('filename')
        logging.info ("Just got the wav as %s" % wav)
        self.put_in_s3(wav)
        logging.info ("I just put the wav in s3")

    def put_in_s3 (self, wav):

        conn = GoogleS3.AWSAuthConnection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        key_name = "testing.wav"

        logging.info ("Puting content in %s in %s bucket" % (key_name, S3_BUCKET_NAME))
        responsedict={}

        logging.info ("really putting stuff in %s %s" % (S3_BUCKET_NAME, key_name))

        audio_type = 'audio/wav'
        

        response = conn.put(
            S3_BUCKET_NAME,
            key_name,
            GoogleS3.S3Object(wav),
        {'Content-Type' : audio_type, 
         'x-amz-acl' : 'public-read'})
        responsedict["response"] = response
        responsedict["url"] = "%s/%s/%s" % (AMAZON_S3_URL, S3_BUCKET_NAME, key_name)
        return responsedict



class CallWorld(webapp.RequestHandler):
    def post(self):
        tropo = tropo_web_api.Tropo()
        options = {}
        options['channel'] = 'TEXT'
        options['network'] = 'SMS'

        tropo.call(MY_PHONE, options)
        tropo.say ("Wish you were here")
        json = tropo.RenderJson()
        logging.info ("Json result: %s " % json)
        self.response.out.write(json)



class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')


def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/hello_tropo.py', TropoDemo),
#                                          ('/hello_tropo.py', CallWorld),
#                                          ('/hello_tropo.py', RecordWorld),
#                                          ('/hello_tropo.py', ExerciseAll),
#                                          ('/hello_tropo.py', ReceiveRecording),
#                                          ('/hello_tropo.py', HelloWorld1),
#                                          ('/hello_tropo.py', RecordMess),
#                                          ('/hello_tropo.py', QuickMessage),
#                                          ('/get_zip_code.py', GetZipCode),
#                                          ('/record.py', RecordMess),
                                          ('/weather.py', Weather),
                                          ('/receive_recording.py', ReceiveRecording),
                                          ('/demo_continue.py', TropoDemoContinue)
  ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
