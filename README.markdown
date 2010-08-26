# Queuable

> Free Background Processing (compared to Heroku and Slicehost)

## Que?

Each worker on Heroku costs $36/mo to run every hour.  There are tricks to make it run more than every hour with DelayedJob, but you still have to pay quite a bit.  What if you wanted to build 10 sample aggregator applications?  $360/month.  With Slicehost, you would just have to pay for a slice ($19-38/mo depending on need), but you'd then have to setup the whole cron/queue system.  So with Queuable I just wanted to take advantage of Google App Engine's built in Cron and Task Queue architecture so you could get them basically for free without doing much work.  Once you really needed a lasting solution, you'd probably go with Heroku's workers.  But by then you'd have some funding :).

So this is 3 things:

1. A minimal Google App Engine application that just handles managing queues and scheduled cron jobs.  You don't need to modify this, you can just deploy it to GAE with `appcfg.py update .` as long as you have a free GAE account.
2. A template Sinatra application which you would use to process what would normally be background processes.  The GAE application sends scheduled tasks to this Sinatra app (on Heroku), you do your feed-fetching or whatever, and the response goes back to GAE.
3. An API.  The last piece is your actual app, say a feed aggregator Rails app with lots of models and controllers.  When you need to do a complex calculation (fetch, parse a large feed), you push that responsibility off to GAE.  You just send it some parameters (hash, string, anything), and it will queue/schedule it, and send it to your Sinatra worker app to take those params and do the operation, freeing your app form time-consuming operations.  When everything's complete, GAE will send the result back to your app for you to save to the database.

## Install

First, you need to get up and running with Google App Engine (I know, I know).  Here's a helpful [getting started with GAE article on Squidoo](http://www.squidoo.com/Google-App-Engine).  I followed [this tutorial](http://www.digitalistic.com/2008/06/09/10-easy-steps-to-use-google-app-engine-as-your-own-cdn/) for setting up GAE as a CDN.

Once you get [Google App Engine installed](http://code.google.com/appengine/downloads.html), open the terminal and check to see if the commands work:

    cd queuable/queue
    appcfg.py update . # deploy app
    dev_appserver.py . # run dev server at http://localhost:8080/
    
Then go to `http://localhost:8080/?params=SOME_KEY` and you will see that task being processed.  To execute the tasks, go here:

[http://localhost:8080/_ah/admin/queues](http://localhost:8080/_ah/admin/queues)

Then click on the task queue name, and click "Run".

## Usage

You need 3 apps to make this work (don't worry, it's easy).

1. Deploy Queuable to Google App Engine with `appcfg.py update .`
2. Create a Sinatra app (or use the Sinatra template in Queuable) that will do all of the intensive processing.
3. Then you have your main app, whatever it is.

Then this is the flow of requests:

1. Your main app makes a `POST` to your Queuable on GAE.  A request might look like this:
        http://my-gae-queuable.appspot.com/url=http://sinatra-worker.heroku.com/handle&params=hello!&calback=http://my-real-app.heroku.com
2. Queuable on GAE will then `POST` to `http://sinatra-worker.heroku.com/handle`, and your Sinatra worker app will receive this:
      {'url': 'http://postable.me', 'callback': 'http://postable.me/posts', 'params': 'hello!'}
3. You then do whatever you want with that data, IN THE REQUEST CYCLE.  We can do it in the request cycle because nobody sees this app.  The whole point is to not use cron/delayed_job on Heroku because it costs money.
4. When you return some result, Queuable on GAE will send this back to the original app:
      {"body"=>"All your content (json, html, xml, anything)", "request"=>"{'url': 'http://postable.me', 'callback': 'http://postable.me/posts', 'params': 'hello!'}", "task"=>"queue", "status"=>"200", "headers"=>"{'content-length': '0', 'set-cookie': 'rack.session=AQz7AA%3D%3D%0A; path=/', 'server': 'nginx/0.6.39', 'connection': 'keep-alive', 'date': 'Thu, 26 Aug 2010 20:30:30 GMT', 'content-type': 'text/html'}"}

This means that your main app just sends a request to GAE and returns immediately.  GAE then queues up the task, and calls your worker app to handle it (so you can program in Ruby).  Whenever it's complete, it sends the processed result back to GAE, and GAE `POST`'s it back to the original app.  So your app isn't tied up in long-running operations, and you don't have to pay lots or configure a ton to have background processes.

## Resources and Notes

- [http://docs.heroku.com/bamboo](http://docs.heroku.com/bamboo)
- [http://code.google.com/appengine/docs/python/taskqueue/overview.html](http://code.google.com/appengine/docs/python/taskqueue/overview.html)
- [http://code.google.com/appengine/docs/python/config/cron.html](http://code.google.com/appengine/docs/python/config/cron.html)
- [http://en.wikipedia.org/wiki/Shared_nothing_architecture](http://en.wikipedia.org/wiki/Shared_nothing_architecture)
- [http://code.google.com/appengine/docs/python/gettingstarted/usingwebapp.html](http://code.google.com/appengine/docs/python/gettingstarted/usingwebapp.html)
- [http://code.google.com/appengine/docs/python/tools/webapp/requestclass.html](http://code.google.com/appengine/docs/python/tools/webapp/requestclass.html)
- [http://code.google.com/appengine/docs/python/urlfetch/overview.html](http://code.google.com/appengine/docs/python/urlfetch/overview.html)
- [http://code.google.com/appengine/docs/python/urlfetch/responseobjects.html](http://code.google.com/appengine/docs/python/urlfetch/responseobjects.html)


One way to describe a mongrel or dyno is as a share-nothing process that consumes web requests. Likewise, a worker can be described as a share-nothing process that consumes jobs from a work queue.

Run heroku jobs scheduling tasks at the end of the previous one.