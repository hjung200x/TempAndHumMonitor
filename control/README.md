32비트 라즈비안 설치할것!!

[계정 생성]
$ sudo adduser hjung
$ sudo passwd hjung

[생성된 계정으로 login]
지금부터는 생성된 계정으로 실행한다.

[파이썬 가상 환경 설치]
$ sudo apt update
$ sudo apt install python3-dev python3-venv python3-pip
$ python -m venv Achamber
$ source Achamber/bin/activate

[필요한 모듈 설치하기]
$ pip install RPi.GPIO
$ pip install Adafruit_DHT
$ pip install smbus2
$ sudo pip install Adafruit_DHT
$ sudo pip install smbus2


[Django, uwsgi, nginx 설치]
$ pip install Django
$ pip install uwsgi
$ sudo apt install nginx

[uwsgi 서비스 등록하기]
$ sudo cp /home/hjung/proj/Achamber/achamber_web/.config/uwsgi/uwsgi.service /etc/systemd/system
$ sudo systemctl daemon-reload
$ sudo systemctl enable uwsgi.service
$ sudo systemctl start uwsgi.service

[nginx 사이트 추가하기]
$ sudo vi /etc/nginx/sites-available/default 에 아래 부분 추가

        location / {
                uwsgi_pass unix:///home/hjung/proj/Achamber/achamber_web/tmp/achamber_web.sock;
                include uwsgi_params;
        }


        location /static/ {
                alias /home/hjung/proj/Achamber/achamber_web/static/;
        }

$ sudo nginx -t
$ sudo systemctl restart nginx

[방화벽 포트 추가하기]
$ sudo apt install ufw
$ sudo ufw delete allow 8000
$ sudo ufw allow 'Nginx Full'


https://wikidocs.net/6611


