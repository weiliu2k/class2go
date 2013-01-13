# should be moved to base, if we need to keep at all
package "python-setuptools" do
    action :install
end

# before we were distributing this ourselves, not anymore.  Remove if there.
bash "clear out /usr/local/bin/ffmpeg" do
    code <<-SCRIPT_END
if [ -e /usr/local/bin/ffmpeg ]; then
    rm /usr/local/bin/ffmpeg
fi
SCRIPT_END
    action run:
end

# we need x264 for video, mp3lame for audio
package "ffmpeg" do
    action :install
end


