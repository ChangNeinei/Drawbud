# team11 ([Drawbud](http://3.16.255.36))

Access URL: http://3.16.255.36
---

Requirements
---
- Django 2.1.5
    `pip3 install django==2.1.5`
- channels (for websockets)
    `pip3 install channels`
- channels_redis (channel layers)
    `pip3 install channels_redis`
- Docker (to run the Redis server version 5.0)
    `docker run -p 6379:6379 -d redis:5.0`

Django server deployment
---
- backend database: MySQL
- create a media directory named `images` under the project root
- follow the instructions on [the tutorial of channels](https://channels.readthedocs.io/en/latest/deploying.html) to start the `daphne` server.
- replace `--fd 0` with `--endpoint fd:fileno=0` on the commandline of `daphne`
- configure the `nginx` server ([reference](https://wyde.github.io/2017/11/24/Deploying-Django-Channels-using-Daphne/))
```
upstream app_server {
    	    server 0.0.0.0:8000;
}
    
server {
	    listen 80;
	    server_name 3.16.255.36; #domain IP

	    location /static {
        	alias /home/ubuntu/team11/drawbud/static;
    	    }
	
	    location / {
		try_files $uri @proxy_to_app;
	    }
	   
	    location @proxy_to_app {
		proxy_pass http://app_server;

		proxy_http_version 1.1;
		proxy_set_header Upgrade $http_upgrade;
		proxy_set_header Connection "upgrade";

		proxy_redirect off;
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Host $server_name;
	    }
	    
}

```
