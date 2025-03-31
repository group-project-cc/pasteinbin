import requests

COUNT = 10_000

HOST = 'localhost'
PORT = 8080

# Get rid of this
for i in range(COUNT):
    print(requests.get(f'http://{HOST}:{PORT}').text)

# Make repeated requests to endpoints created in the API server
# Maybe spawn a thread per endpoint and just spam? Or use multiprocessing
