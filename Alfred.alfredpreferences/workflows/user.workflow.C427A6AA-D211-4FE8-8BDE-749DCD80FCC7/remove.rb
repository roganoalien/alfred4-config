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

feedback = Feedback.new

if File.exist?(PATH)
		
	oldDrives.each_with_index do |name, index|
		
		feedback.add_item({
			:title => name,
			:subtitle => "Press ENTER to remove from list",
			:autocomplete => "#{name}",
			:arg => name,
			:icon => {:type => "filetype", :name => "49BB84EE-8158-4CE3-9C09-0141E3835AD7.png"}
		})
	end
else
	feedback.add_item({
		:title => "No NTFS enabled drives.",
		:autocomplete => '',
		:valid => 'no',
		:icon => {:type => "filetype", :name => "49BB84EE-8158-4CE3-9C09-0141E3835AD7.png"}
	})
end

puts feedback.to_xml