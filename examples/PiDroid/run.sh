!#bin/sh
cd ../../mjpg-streamer/mjpg-streamer/
./start.sh &
cd ../../examples/Robot\ stuff/
sudo python PiDroid.py 0.0.0.0 $1
