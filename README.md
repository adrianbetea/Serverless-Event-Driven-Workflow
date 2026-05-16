# Virtual Campus: Serverless Event-Driven Workflow

[![AWS](https://img.shields.io/badge/AWS-Serverless-FF9900?logo=amazonaws)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/)
[![DevOps](https://img.shields.io/badge/Course-DevOps_Master-004D99)](#)

> **Project P12:** Build a serverless event-driven workflow. 
> **Author:** Adrian-Vlad Betea

## Project Overview
This repository contains the implementation of a fully functional **Virtual Campus Portal** built on an enterprise-grade, decoupled asynchronous microservice architecture. It demonstrates key DevOps and Cloud Computing concepts, including Event-Driven Workflows, CQRS (Command and Query Responsibility Segregation), Idempotency, and Serverless Cost Optimization.

Students can use the HTML frontend to log in, view their assigned courses, and enroll in new ones.

## System Architecture

```mermaid
graph LR
    %% Defining the styles for AWS components
    classDef frontend fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef api fill:#e8c6ff,stroke:#8c44c2,stroke-width:2px;
    classDef lambda fill:#ffad66,stroke:#e67300,stroke-width:2px;
    classDef queue fill:#ffb3d9,stroke:#cc0066,stroke-width:2px;
    classDef db fill:#99ddff,stroke:#0077b3,stroke-width:2px;

    %% Nodes
    UI["💻 Student Browser<br/>(Vanilla JS)"]:::frontend
    API["🌐 API Gateway<br/>(HTTP Trigger)"]:::api
    L1["⚡ Lambda 1<br/>(Producer)"]:::lambda
    SQS["📥 Amazon SQS<br/>(Event Queue)"]:::queue
    L2["⚡ Lambda 2<br/>(Worker)"]:::lambda
    DB["🗄️ DynamoDB<br/>(NoSQL)"]:::db

    %% Connections and Data Flow
    UI -- "1. Load Dashboard (GET)" --> API
    UI -- "3. Enroll in Course (POST)" --> API
    
    API --> L1
    
    L1 -. "2. Read Courses (Fast)" .-> DB
    L1 -- "4. Send Message (Async)" --> SQS
    
    SQS -- "5. Trigger Event" --> L2
    
    L2 -- "6. Write/Append Course" --> DB

    %% Notes
    style UI stroke-dasharray: 5 5
