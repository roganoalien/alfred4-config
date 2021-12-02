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

entry = 'LABEL=' + drive + ' none ntfs rw,auto,nobrowse'
File.open(PATH, 'a') { |file| file.puts entry }

disk = `diskutil list | grep "#{name}"`

disk = disk.split(' ')

`diskutil unmount /dev/#{disk.last}`
`diskutil mount /dev/#{disk.last}`
`open "/Volumes/#{name}"`

puts name + ' added to NTFS enabled list.'