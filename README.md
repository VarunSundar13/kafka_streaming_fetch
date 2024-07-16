## Prerequisites

- Docker and Docker Compose
- Python 3.7+
- pip (Python package manager)

## Setup

1. Clone Repo:
git clone ...


2. Install Dependency:
pip install kafka-python
NOTE: if using python 3.12 there is an issue with kafka-python, use kafka-python-ng instead

3. Start the Kafka environment:
docker-compose up -d

## Running the Pipeline
0. Make sure docker is running

1. Run the consumer-producer script:
python src/consumer_producer.py

The script will start processing messages from the 'user-login' topic, sending processed data to the 'processed-logins' topic, and periodically sending insights to the 'login-insights' topic.

3. To stop the script, use Ctrl+C.

4. View processed logins:
Open another terminal window and run:
python src/processed_logins.py

You should start seeing processed login messages appearing in this window.

5. View login insights:
Open one more terminal window and run:
python src/login_insights.py
You should see login insights appearing periodically in this window (remember, insights are generated every 100 messages in the example code).


The consumer_producer.py window shows processing data and generated insights.
The processed_logins.py window shows processed login data
The login_insights.py window shows periodic insights about device types, hourly trends, etc.


6. Shutdown and cleanup:
When you're done testing, you can stop all the processes:

Use Ctrl+C in each of the Python script windows to stop the scripts.
Stop the Docker containers with:
docker-compose down


## DATA FLOW EXPLANATION
A data generator creates a 'user-login' Kafka topic. It then produces login data for a user, sending it to that topic. Our Python script comes along and consumes those login messages. When it has a login message, it tries to perform some simple analytics on it. The script then passes that message along to a new Kafka topic that it creates called 'processed-logins'. This is going to be for the data that has been "cleaned up" or is "tried and true" (and should be a subset of what has gone into 'user-login'). Every so often, a "login insight" is sent to the 'login-insights' topic.

These are the jobs that the script does: It determines the login count for each device type. It combines the login count for each device type over each hour (to get something like a house next to ... not sure how this finishes). It keeps track of the unique IP addresses per user. It figures out the total number of IP addresses used by each user. It constantly comes up with "periodic" developments in device usage and logins.

## DESIGN CHOICE
The reason we use Kafka is its high level of competence for achieving real-time, high-throughput data stream handling. Setting up Kafka on Docker is very straightforward. 
Kafka ensures scalability, partitioning topics across different machines in a cluster. It also allows applications to work together on consuming and parallel processing. It's designed to handle failures while maintaining its core operation.

## SCALING UP
To allow more parallel data processing, boost the count of Kafka partitions. Group consumers into multiple instances of a processing script. Also depending on how large we scale up, the engineer should consider using a more capable framework, like Apache Spark as it is better at handling large volumes of data.

## CHANGES FOR PRODUCTION 
First adding both unit and integration tests for the code would be important to make sure everything works as expected.

Schema Registry can help ensure data consistency and Kafka connect can be used to interface with external systems. Moreover, it would be important to orchestrate docker instances with something like Kubernetes. 

Finally implementing proper network security, VPCs and secrets management to ensure security of the production app would also be important.

