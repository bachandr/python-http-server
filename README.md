# python-http-server

HTTP server with key value store in python

Usage:
```
python3 ./http-server.py [<port>]
```

| Description | Command |
| ------ | ------ |
| Send a GET request to retrieve all key value | curl -v -XGET http://localhost:{port}/store/key |
| Send a GET request to retrieve value for given key | curl -v -XGET http://localhost:{port}/store/key/{key} |
| Send a DELETE request to delete all key value | curl -v -XDELETE http://localhost:{port}/store/key |
| Send a DELETE request to delete entry for given key | curl -v -XDELETE http://localhost:{port}/store/key/{key} |
| Send a POST/PUT request to store key value | curl -v -XPOST "http://localhost:{port}/store/key/key}/value/{value}" -d '{}' |
