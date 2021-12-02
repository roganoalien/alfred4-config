require File.join(File.dirname(__FILE__), 'alfred_feedback.rb')

class String
  def string_between_markers marker1, marker2
    self[/#{Regexp.escape(marker1)}(.*?)#{Regexp.escape(marker2)}/m, 1]
  end
end

PATH = '/etc/fstab'

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

	if not oldDrives.include? name
	
		feedback.add_item({
			:title => name,
			:autocomplete => name,
			:arg => name,
			:icon => {:type => "filetype", :name => "4AF9B2F9-D9AD-4348-8089-9C7786020D30.png"}
		})
	end

end

if feedback.to_xml == '<items/>' and drives.count == 0

	feedback.add_item({
		:title => 'No NTFS drives found.',
		:autocomplete => '',
		:valid => 'no',
		:icon => {:type => "filetype", :name => "4AF9B2F9-D9AD-4348-8089-9C7786020D30.png"}
	})

elsif feedback.to_xml == '<items/>' and drives.count > 0
	feedback.add_item({
		:title => 'No new NTFS drives found.',
		:subtitle => 'All mounted NTFS drives already have Write enabled.',
		:autocomplete => '',
		:valid => 'no',
		:icon => {:type => "filetype", :name => "4AF9B2F9-D9AD-4348-8089-9C7786020D30.png"}
	})
end

puts feedback.to_xml