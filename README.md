# yamdb_final
API-project running across multiple Docker containers. YamDB allows you to leave reviews, ratings and comments on creation

![workflow yamdb_final](https://github.com/fattybobcat/yamdb_final/workflows/yamdb/badge.svg)

This project will allow you to deploy to your "empty" server - YamDB project

## Getting Started

These instructions will get you a copy of the project up and running on your work-machine.
See deployment for notes on how to deploy the project on a live system. 

### Prerequisites

* Create your own mail for the project, which will send a verification code to confirm users (Better gmail)

### Containers

The stack uses Python, Postgres for storage and Nginx.

## INSTALLATION

- Copy this repository to your local machine;
- Create Actions secrets in Github:
  ```
    Name                    Value                           Comments
    DB_ENGINE           =   django.db.backends.postgresql  # indicate that we are working with postgresql
    DB_NAME             =   postgres                       # database name
    POSTGRES_USER       =   login                          # login to connect to the database
    POSTGRES_PASSWORD   =   password                       # password to connect to the database (set your own)
    DB_HOST             =   db                             # service (container) name
    DB_PORT             =   5432                           # port for connecting to the database
    MAIL_SENDER         =   youremail                      # mail for sending confirmation code
    PASSWORD_MAIL_SENDER=   yourpassword                   # password for mail
    HOST_YC             =   xxx.xxx.xxx.xxx                # ip adress your server
    USER_YC             =                                  # username to connect to the server 
    SSH_KEY_PR          =   ---begin---                    # private key from a computer that has access to the production server (cat ~/.ssh/id_rsa) 
    PASSPHRASE          =                                  # If you used a passphrase when creating the ssh key, then add the variable 
    TELEGRAM_TO         =   your id telegram               # id your Telegram accaunt to which the message will be sent, about the status of the worlkflow assembly (you can ask @userinfobot)  
    TELEGRAM_TOKEN      =   Token                          # token your telegram-bot (you can ask  @BotFather)
    DOCKER_USERNAME     =                                  # your docker name
    DOCKER_PASSWORD     =                                  # your docker password 
  ```
- Push your projects to your Git repo;
- Wait workflow result; If not error - Great! Server is running on your server! Now you can rebild base, create superuser!

## Settings

There is no data in our database now. Need to install migrations and write test database

1. Open a new terminal and connect to your server:
```
  ssh your_login@yor.up.adr.ess
```
2. Run:
```
  docker container ls
```
  You will see next (example):
```
5652f89da934   nginx:1.19.6              "/docker-entrypoint.…"   23 hours ago   Up 23 hours   0.0.0.0:80->80/tcp   code_nginx_1
5ed74b986dda   fattybobcat/yamdb:v1.21   "/bin/sh -c 'gunicor…"   23 hours ago   Up 23 hours                        code_web_1
2622b38c26ce   postgres:12.4             "docker-entrypoint.s…"   23 hours ago   Up 23 hours   5432/tcp             code_db_1
```
2. Go to the directory where the given project is stored and run the following command to copy the database dump fixture.json to the project need app:
  ```
  docker cp  fixture.json <CONTAINER ID>
  ```
3. To enter the web container (fattybobcat/yamdb:v1.21): run `docker exec -it <CONTAINER ID> bash`
4. Make migrate `python manage.py migrate`
5. To load the database run the commands:
```
  python3 manage.py shell
# execute in the opened terminal:
>>> from django.contrib.contenttypes.models import ContentType
>>> ContentType.objects.all().Delete()
>>> quit()

python manage.py loaddata dump.json
```

### Create superuser:

1. To enter the web container (fattybobcat/yamdb:v1.21): run `docker exec -it <CONTAINER ID> bash`
2. Run the commands: `python manage.py createsuperuser`

## Site
[site](http://84.201.140.114)

## OpenAPI specification:
[redoc](http://84.201.140.114/redoc/)

## Authors
Petruk Aleksandr - Python Developer

## License
This project is licensed under the MIT License
