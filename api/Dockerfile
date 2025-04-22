FROM python:3

COPY ./api.py /api.py

RUN pip install Flask prometheus_client Flask Flask-RESTful Flask-CORS gunicorn requests prometheus_client Flask-JWT-Extended flask_bcrypt confluent-kafka

WORKDIR /
CMD ["python", "/api.py"]
# CMD ["flask", "run", "--app", "api"]
