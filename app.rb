require 'rubygems'
require 'sinatra'
require 'broadway'
require 'haml'
require 'json'

this = File.expand_path(File.dirname(__FILE__))
SITE = Broadway.build(:source => "#{this}/_content", :settings => "#{this}/_config.yml")

enable :sessions
set :public, this
set :views, "views"

get "/" do
  "HELLO"
end

post "/queue" do
  puts "=== REQUEST ==="
  puts request.inspect
  puts "=== PARAMS ==="
  puts params.inspect
  ""
end

post "/cron" do
  puts "POSTED TO /posts"
  puts "=== REQUEST ==="
  puts request.inspect
  puts "=== PARAMS ==="
  puts params.inspect
  ""
end