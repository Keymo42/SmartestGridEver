sudo lsof -t -i udp:8082 | xargs sudo kill -9 &
sudo lsof -t -i udp:8083 | xargs sudo kill -9 &
sudo lsof -t -i udp:8084 | xargs sudo kill -9