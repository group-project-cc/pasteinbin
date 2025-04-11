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
