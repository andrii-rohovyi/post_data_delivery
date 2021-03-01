# post_data_delivery
Backend for optimization logistic business

### Running the service in Docker container
To build container: sudo docker build -t logistic . 
Run Docker sudo docker run --env-file env-variable.env -p 8080:8080 logistic
To stop Docker containers: docker stop $(docker ps -a -q)
### Running the service locally
Example of local service running: `python3 main.py`
### Example of POST query
Query for client: curl -X POST -d @example.json http://localhost:8080
### Check unit tests before each PR
`python -m pytest tests `