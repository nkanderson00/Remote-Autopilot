raspivid -n -t 0 -cd MJPEG -w 160 -h 90 -fps 30 -b 1000000 -o - | gst-launch-1.0 fdsrc ! "image/jpeg,framerate=30/1" ! jpegparse ! rtpjpegpay ! udpsink host=68.134.229.20 port=8000 &
sudo python3 client.py
