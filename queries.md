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

```sh
histogram_quantile(0.95, sum(rate(http_response_time_seconds_bucket[10m])) by (le, endpoint))
```

### QUERIES FOR MOST FREQUENT ERRORS IN THE APPLICATION

[INSERT SOMETHING]
