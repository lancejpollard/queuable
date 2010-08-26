require 'rubygems'
require 'sinatra'
require 'haml'
require 'json'

set :port, 4567

get "/" do
  haml :index
end

post "/" do
  feed = JSON.parse(params["body"])
  puts "=== Save this to the Database! ==="
  puts feed.inspect
  puts "=================================="
  ""
end

__END__
@@ layout
!!! 5
%html{:lang => "en-US", :xmlns => "http://www.w3.org/1999/xhtml"}
  %head
    %title Queuable Demo
  %body
    = yield
    
@@ index
%form{:action => "http://localhost:8080/", :method => :get}
  %input{:type => :hidden, :name => :callback, :value => "http://localhost:4567/"}
  %input{:type => :hidden, :name => :url, :value => "http://localhost:4568/queue"}
  %input{:type => :text, :name => :feed, :value => "http://feeds.feedburner.com/RubyInside"}
  %input{:type => :submit, :value => "Update Feed"}