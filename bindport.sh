socat -d -d -v pty,link=/tmp/ttyRover,raw,echo=0 udp:192.168.2.1:5000,sourceport=5000
