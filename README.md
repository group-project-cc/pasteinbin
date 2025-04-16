# Pasteinbin!

A pastebin alternative written for Cloud Computing project by:

PES2UG22CS393
PES2UG22CS902
PES2UG22CS416
PES2UG22CS384

## Deploy API server

```sh
$ flask --app api/api run -h localhost -p 8080
```

## Prerequisites for running Kafka
- Docker<br>
  Make sure Docker Desktop is running in background (if you're on windows/mac). if you face any issues with docker on terminal, maybe try logging in first?
  ```sh
      $ docker login -u <docker_username> -p <docker_password>
  ```
      
  
- confluent-kafka
```sh
$ pip install confluent-kafka
```

#### Steps
<br>

1. Start Kafka Stack.
```sh
$ docker compose up --build
```
<br>

2. Run the *docker_topics.py* file.
```sh
$ python docker_topics.py
```
<br>

3. Start the flask *api.py* file.
```sh
$ flask --app api run
```
<br>

4. Run the simple consumer *basic.py* file.
```sh
$ python basic.py
```
<br>

5. Run the api *spammer.py* file.
```sh
$ python spammer.py
```
<br>

Good to go :D

<br>
P.S: When you're done, use 

```sh
$ docker compose down
```
<br>

*or*

<br>

```sh
$ docker compose down -v
```
This one in particular removes the containers and clears the persistent data in the volume so no useless logs remain or are persisted.

<br>

## --IN PARTICULAR FOR POSTGRESQL AND PGADMIN--

- Run the docker compose file as mentioned previously.
- Run the docker_topics.py file.
- Run *postgre_schema.py*
```sh
$ python run postgre_schema.py
```
This creates the tables in the database, ready to be filled with logs.

<br>

pgadmin is a postegresql visualisation tool (GUI basically) that helps you verify if everything's fine.
To access that:
- Go to localhost:8080
- email: admin@admin.com <br>
  password: admin
- Click on 'Add New Server'. (unless somehow it already exists there on left sidebar o_o)
- Give a name for your Server.
- Move to the "Connection Tab". <br>


  Hostname: postgres <br>
  Port: 5432 <br>
  Maintenance Database: logs_db <br>
  username: admin <br>
  password: password 
- Save.

You got it :) <br> You can navigate to the server, look for logs_db and check if everything's fine. You can also run sql commands by clicking on logs_db and navigating towards the 'cylinder with a triangle' icon. That's your Query Tool (essentially SQL shell). Run commands. Check if logs are present. Have a bun samosa 🍔

(Should misfortune befall you, here's a 15 min video on using pgadmin: https://youtu.be/WFT5MaZN6g4?si=36_71O4zve2JD7vC)
  
  
