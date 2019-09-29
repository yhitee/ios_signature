require "spaceship"
require 'pathname'
require 'mysql2'
# -*- coding: UTF-8 -*-

account_username = ARGV[0]
account_password = ARGV[1]
name = ARGV[2]
udid = ARGV[3]
username = ARGV[4]
bundid_after = ARGV[5]
appid_name = ARGV[6]

dir_path = Pathname.new(File.dirname(__FILE__)).realpath

Spaceship.login("#{account_username}","#{account_password}")
device = Spaceship.device.create!(name: "#{name}", udid: "#{udid}")

app = Spaceship.app.find("#{bundid_after}")
if app
    profiles_adhoc = Spaceship.provisioning_profile.ad_hoc.all.find { |p| p.name == "#{appid_name}" }
    profiles_adhoc.devices = Spaceship.device.all
    profiles_adhoc.update!
    profile = Spaceship.provisioning_profile.ad_hoc.all.find { |p| p.name == "#{appid_name}" }
    File.write("#{dir_path}/#{username}/#{appid_name}.mobileprovision",profile.download)
else
    new_app = Spaceship.app.create!(bundle_id:"#{bundid_after}",name:"#{appid_name}")
    cert = Spaceship::Portal.certificate.production.all.first
    Provision_profile = Spaceship.provisioning_profile.ad_hoc.create!(bundle_id:"#{bundid_after}",certificate:cert,name:"#{appid_name}")
    File.write("#{dir_path}/#{username}/#{appid_name}.mobileprovision",Provision_profile.download)
end

devices_count = Spaceship.device.all.length
client = Mysql2::Client.new(:host => "",
                            :username => "",
                            :password => '',
                            :port =>"",
                            :database => ""
                            )
client.query("update ios_distribute_developeraccount set used_devices_count=#{devices_count} where username=\"#{account_username}\"")
