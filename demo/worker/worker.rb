require 'rubygems'
require 'sinatra'
require 'json'
require 'feedzirra'

set :port, 4568

before do
  puts "=== PARAMS ==="
  puts params.inspect
  puts "=============="
end

post "/queue" do
  feed = Feedzirra::Feed.fetch_and_parse("http://feeds.feedburner.com/RubyInside")
  feed.to_json
end

post "/cron" do
  "a scheduled task was run"
end
