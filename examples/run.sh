!#bin/sh
cd ../mjpg-streamer/mjpg-streamer/
./start.sh &
cd ../../examples/
sudo python regular.py 0.0.0.0 $1
