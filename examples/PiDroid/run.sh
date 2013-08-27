!#bin/sh
cd ../../mjpg-streamer/mjpg-streamer/
./start.sh &
cd ../../examples/PiDroid
sudo python robot.py
