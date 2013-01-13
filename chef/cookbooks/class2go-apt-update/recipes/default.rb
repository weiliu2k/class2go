# we need a version of ffmpeg that includes the libx264 video codec and
# libmp3lame audio codecs. This guy's seems to be referenced by others
# and well maintained.

execute "jon-severinsson ppa for ffmpeg" do
    command "add-apt-repository -y ppa:jon-severinsson/ffmpeg" do
    user "root"
    action :run
end

execute "apt-get update" do
    command "apt-get update -q -y"
    returns [0, 100]
    action :run
end

# execute "apt-get upgrade" do
    # command "apt-get upgrade -q -y"
    # action :run
# end

