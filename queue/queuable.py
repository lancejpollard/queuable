import logging
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
import urllib

class QueueHandler(webapp.RequestHandler):
  def get(self):
    url = self.request.get("url")
    params = self.request.get("params")
    callback = self.request.get("callback") or self.request.referrer
    # Add the task to the default queue.
    taskqueue.add(url = "/queue", params = {"params":str(params), "url":str(url), "callback":str(callback)})
    
    self.response.headers["Content-Type"] = "text/plain"
    self.response.out.write("queued")

class QueueWorker(webapp.RequestHandler):
  def post(self): # should run at most 1/s
    url = self.request.get("url")
    params = self.request.get("params")
    callback = self.request.get("callback")
    body = {
      "url": str(url),
      "callback": str(callback),
      "params": str(params)
    }
    # post to the service you want to do the processing
    result = urlfetch.fetch(url = url, payload = body, method = urlfetch.POST, headers = {'Content-Type': 'application/x-www-form-urlencoded'})
    # post the response back to your app
    body = {
      "status": result.status_code,
      "headers": str(result.headers),
      "body": result.content,
      "task": "queue",
      "request": body
    }
    body = urllib.urlencode(body)
    result = urlfetch.fetch(url = callback, payload = body, method = urlfetch.POST, headers = {'Content-Type': 'application/x-www-form-urlencoded'})
    
class CronWorker(webapp.RequestHandler):
  def get(self): # should run at most 1/s
    url = self.request.get("url")
    params = self.request.get("params")
    callback = self.request.get("callback")
    body = {
      "url": str(url),
      "callback": str(callback),
      "params": str(params)
    }
    # post to the service you want to do the processing
    result = urlfetch.fetch(url = url, payload = body, method = urlfetch.POST, headers = {'Content-Type': 'application/x-www-form-urlencoded'})
    # post the response back to your app
    body = {
      "status": result.status_code,
      "headers": str(result.headers),
      "body": result.content,
      "task": "queue",
      "request": body
    }
    body = urllib.urlencode(body)
    result = urlfetch.fetch(url = callback, payload = body, method = urlfetch.POST, headers = {'Content-Type': 'application/x-www-form-urlencoded'})

def main():
  run_wsgi_app(webapp.WSGIApplication([
    ("/", QueueHandler),
    ("/queue", QueueWorker),
    ("/cron", CronWorker),
  ]))

if __name__ == "__main__":
  main()