## QUERIES FOR REAL-TIME LOGS

- REQUEST_LOGS

```sh
SELECT
  timestamp,
  endpoint,
  method,
  status_code,
  response_time_ms
FROM request_logs
WHERE to_timestamp(timestamp / 1000.0) > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC
LIMIT 100
```

- AUTH_LOGS

```sh
SELECT
 id,
 event,
 username,
 timestamp,
 result,
 endpoint,
 method,
 status_code
FROM auth_logs
WHERE to_timestamp(timestamp / 1000.0) > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC
LIMIT 100
```

- PASTE_LOGS

```sh
SELECT
 id,
 event,
 username,
 paste_id,
 content,
 timestamp,
 result,
 endpoint,
 method,
 status_code
FROM paste_logs
WHERE to_timestamp(timestamp / 1000.0) > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC
LIMIT 100
```

- ACCESS_LOGS

```sh
SELECT
 id,
 event,
 username,
 timestamp,
 endpoint,
 method,
 keyword
 status_code
FROM access_logs
WHERE to_timestamp(timestamp / 1000.0) > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC
LIMIT 100
```

### QUERIES FOR REQUEST COUNT PER ENDPOINT

```sh
sum(rate(http_requests_total[5m])) by (endpoint, method, status_code)
```

### QUERIES FOR RESPONSE TIME TRENDS

- AVERAGE RESPONSE TIME IN THE LAST HOUR

```sh
SELECT
  date_trunc('minute', to_timestamp(timestamp / 1000.0)) AS time_interval,
  AVG(response_time_ms) AS avg_response_time
FROM request_logs
WHERE to_timestamp(timestamp / 1000.0) > NOW() - INTERVAL '1 hour'
GROUP BY time_interval
ORDER BY time_interval DESC
```

- MAXIMUM RESPONSE TIME PER INTERVAL

```sh
SELECT
  date_trunc('minute', to_timestamp(timestamp / 1000.0)) AS time_interval,
  MAX(response_time_ms) AS max_response_time
FROM request_logs
WHERE to_timestamp(timestamp / 1000.0) > NOW() - INTERVAL '1 hour'
GROUP BY time_interval
ORDER BY time_interval DESC
```

- MINIMUM RESPONSE TIME PER INTERVAL

```sh
SELECT
  date_trunc('minute', to_timestamp(timestamp / 1000.0)) AS time_interval,
  MIN(response_time_ms) AS min_response_time
FROM request_logs
WHERE to_timestamp(timestamp / 1000.0) > NOW() - INTERVAL '1 hour'
GROUP BY time_interval
ORDER BY time_interval DESC
```

- REQUEST COUNT AND RESPONSE TIME AVERAGE

```sh
SELECT
  date_trunc('minute', to_timestamp(timestamp / 1000.0)) AS time_interval,
  COUNT(*) AS request_count,
  AVG(response_time_ms) AS avg_response_time
FROM request_logs
WHERE to_timestamp(timestamp / 1000.0) > NOW() - INTERVAL '1 hour'
GROUP BY time_interval
ORDER BY time_interval DESC
```

### QUERIES FOR MOST FREQUENT ERRORS IN THE APPLICATION

[INSERT SOMETHING]
