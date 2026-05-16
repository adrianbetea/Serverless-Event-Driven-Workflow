#  Virtual Campus: Serverless Event-Driven Workflow

[![AWS](https://img.shields.io/badge/AWS-Serverless-FF9900?logo=amazonaws)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/)
[![DevOps](https://img.shields.io/badge/Course-DevOps_Master-004D99)](#)

> **Project P12:** Build a serverless event-driven workflow. 
> **Author:** Adrian-Vlad Betea

## Project Overview
This repository contains the implementation of a fully functional **Virtual Campus Portal** built on a decoupled, asynchronous microservice architecture. It demonstrates key DevOps and Cloud Computing concepts, including Event-Driven Workflows, Idempotency, Serverless Cost Optimization, and the Cold Start phenomenon.

Students can use the HTML frontend to log in, view their assigned courses, and enroll in new ones, all processed entirely via serverless cloud functions.

## System Architecture

![System Architecture](`./System Architecture.png`) 

### Technology Stack & Components
The architecture relies entirely on AWS managed services, requiring zero server provisioning:
* **Frontend UI:** A vanilla HTML/JS page simulating the Virtual Campus, featuring a built-in timer (`performance.now()`) to monitor API latency.
* **Amazon API Gateway:** The entry point that intercepts HTTP requests from the browser.
* **AWS Lambda 1 (Producer/API):** A Python 3.14 function that receives requests. It either reads data directly from the database or sends new enrollment requests to a message queue.
* **Amazon SQS (Simple Queue Service):** A message queue acting as an asynchronous buffer to prevent database bottlenecks.
* **AWS Lambda 2 (Worker):** A background Python 3.14 function triggered automatically by SQS events to safely append data to the database.
* **Amazon DynamoDB:** A NoSQL database storing student profiles and their respective enrolled courses.

## How It Works (The Workflows)
To ensure scalability during high traffic (e.g., hundreds of students enrolling simultaneously), the application strictly separates reading data from writing data:

* **Synchronous Read Workflow:** When a student logs in or clicks "Refresh", an HTTP `GET` request is routed via API Gateway to **Lambda 1**. The function connects directly to DynamoDB and instantly returns the student's enrolled courses to the UI.
* **Asynchronous Write Workflow:** When a student clicks "Enroll", an HTTP `POST` request triggers **Lambda 1**. Instead of writing to the database directly, Lambda 1 packages the data into a JSON message, drops it into **Amazon SQS**, and replies `200 OK` instantly to the user. The queue message acts as an event that automatically triggers **Lambda 2** (the Worker) in the background to securely update DynamoDB.

## Key DevOps Concepts & Challenges Solved

### 1. The "Cold Start" Phenomenon
In a serverless environment, AWS does not keep servers running when there is no traffic. Performance metrics were tracked directly in the frontend UI to observe container provisioning:
* **Cold Start:** When a new request arrives after a period of inactivity, AWS provisions a new container and loads the Python environment. Executions typically take **1000ms to 2000ms**.
* **Warm Start:** Subsequent requests reuse the "warm" container kept in memory, dropping the execution time drastically to **80ms to 160ms**.

### 2. Idempotency & Race Condition Prevention
A critical issue discovered during testing was that if a student clicked "Enroll" rapidly, duplicate messages were sent to the queue, resulting in duplicate courses. This was solved using a multi-layered defense:
* **Database Lock:** `Lambda 2` utilizes a strict DynamoDB `ConditionExpression`. The database strictly rejects the update if the specific course is already in the student's list.
* **Client-Side Validation:** The UI temporarily disables the enroll button and checks the local interface to prevent redundant AWS requests (Fail-Fast pattern).

### 3. Serverless Cost Implications
* **Zero Idle Cost:** Unlike traditional EC2 instances that bill an hourly rate, this architecture costs **$0.00** when no students are using the portal.
* **Pay-As-You-Go:** AWS bills strictly for the number of requests and the execution duration (in milliseconds). Because `Lambda 1` delegates the heavy writing process to the SQS queue and closes quickly, compute costs are kept to an absolute minimum.

### 4. Security and IAM (Zero-Trust)
By default, AWS services cannot communicate with each other. Following the *Principle of Least Privilege*, specific IAM Execution Roles were created:
* **Lambda 1 Role:** Granted permission to write to SQS and read from DynamoDB.
* **Lambda 2 Role:** Granted the `AWSLambdaSQSQueueExecutionRole` policy to be triggered by the queue, and permissions to write to DynamoDB.

### 5. CORS Configuration
Because the local frontend HTML file communicates with an external AWS API domain, the browser blocked requests for security reasons. This was solved by explicitly injecting the `Access-Control-Allow-Origin: *` headers into the Lambda Python response to allow Cross-Origin Resource Sharing.
