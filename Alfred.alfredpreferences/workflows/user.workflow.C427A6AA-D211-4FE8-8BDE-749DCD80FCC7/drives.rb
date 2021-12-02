require 'yaml'
require File.join(File.dirname(__FILE__), 'alfred_feedback.rb')

class String
  def string_between_markers marker1, marker2
    self[/#{Regexp.escape(marker1)}(.*?)#{Regexp.escape(marker2)}/m, 1]
  end
end

PATH = '/etc/fstab'

arg = ARGV[0]

oldDrives = []

if File.exist?(PATH)

	File.open(PATH, "r").each_line do |line|
	 	name = line.string_between_markers('=', ' ')
		
		if name.include? '\040'
			name.gsub!('\040', ' ')
		end
	
		oldDrives.push(name)
	end
end
	
list = `df -T ntfs | grep /dev/`

list = list.split(/(\n)/)

drives = []

list.each do |name|

	drive = name.split('/').last
	if drive =~ /\n/
		next
	end
	
	drives.push(drive)
end

feedback = Feedback.new

drives.each do |name|

	if oldDrives.include? name
	
		feedback.add_item({
			:title => name,
			:subtitle => "Open in Finder",
			:autocomplete => name,
			:arg => name,
			:icon => {:type => "filetype", :name => "icon.png"}
		})
	end

end

if feedback.to_xml == '<items/>'

	feedback.add_item({
		:title => 'No mounted NTFS drives found.',
		:subtitle => 'You have to enable NTFS write first. Try: "ntf enable"',
		:autocomplete => '',
		:valid => 'no',
		:icon => {:type => "filetype", :name => "icon.png"}
	})

end

puts feedback.to_xml