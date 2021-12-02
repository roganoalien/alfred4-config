class String
  def string_between_markers marker1, marker2
    self[/#{Regexp.escape(marker1)}(.*?)#{Regexp.escape(marker2)}/m, 1]
  end
end

PATH = '/etc/fstab'

drive = ARGV[0].dup
name = drive.dup

if drive.include? ' '
	drive.gsub!(' ', '\\\040')
end

oldDrives = []

if File.exist?(PATH)

	File.open(PATH, "r").each_line do |line|
		line = line.string_between_markers('=', ' ')
		oldDrives.push(line)
	end
end

if not oldDrives.include? drive

	entry = 'LABEL=' + drive + ' none ntfs rw,auto,nobrowse'
	File.open(PATH, 'a') { |file| file.puts entry }
	
	puts name + ' added to NTFS enabled list.'

elsif oldDrives.include? drive
	
	 	removed = false
	    output = String.new

	    File.open(PATH, "r").each_line do |line|
	
			  line = line.string_between_markers('=', ' ')
	        if line == drive
	            removed = true
	        else
					line = 'LABEL=' + line + ' none ntfs rw,auto,nobrowse'
	            output << line
	        end
	    end
	
		if output == ''
			File.delete(PATH)
		else
			if removed
		       File.open(PATH, 'w') { |file| file.puts output }
		   end
		end
		
		puts name + ' removed from NTFS enabled list.'
end