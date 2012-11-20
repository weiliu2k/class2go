We distribute ffmpeg ourselves since we need a version that can use
the libx264 and MP3 codec.  Instead of compiling and staticly linking
with those libraries, you can just install binary packages for those
and dynamically link with them.

Binary checked in here was compiled on Ubuntu 12.4 LTS machine
(util10.prod.c2gops.com).  Method:

sudo apt-get install libx264-dev libmp3lame-dev

git clone git://git.videolan.org/ffmpeg.git 
cd ffmpeg
./configure --enable-libx264 --enable-libmp3lame --enable-gpl --prefix=/usr/local
make 


To install on a Mac, use "brew install ffmpeg".  The standard ffmpeg
comes with x264 and lame compiled in.  Go figure.

