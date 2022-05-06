gst-launch-1.0 udpsrc port=8000 ! "application/x-rtp,encoding-name=(string)JPEG" ! rtpjpegdepay ! decodebin ! autovideosink
python3 ./joystick/control.py
