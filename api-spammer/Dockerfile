FROM python:3

COPY ./spammer.py /spammer.py

RUN pip install requests

WORKDIR /
CMD ["python", "/spammer.py"]
