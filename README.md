# Multi-Container Service with Producer, RabbitMQ, and Consumer

This project demonstrates a multi-container service consisting of a Producer, a RabbitMQ queue, and a Consumer. The Producer is a web service that accepts a JSON payload via a POST request, validates it, and pushes the message to the RabbitMQ queue. The Consumer reads messages from the RabbitMQ queue, processes them, and appends them to a CSV file.

## Prerequisites

- Docker
- Docker Compose

## Project Structure

The project is organized into the following directories:

- `producer`: Contains the web service that processes incoming JSON payloads and pushes them to the RabbitMQ queue.
- `queue`: RabbitMQ
- `consumer`: Contains the service that reads messages from the RabbitMQ queue and appends them to a CSV file.
- `data`: Stores the output CSV file.

The root directory contains the `docker-compose.yml` file that orchestrates the multi-container service.

## Setup

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-name>

2. Initialize the output.csv file in the data directory with the headers:
    `device_id,client_id,created_at,license_id,image_frame,prob,tags`

3. Build and run the services using Docker Compose:
    `docker-compose up --build`


    This command will build the Producer and Consumer containers

## Usage
Send a POST request to the Producer at http://localhost:5000/ with a JSON payload in the following format:

    ```json
{
    "device_id": "string",
    "client_id": "string",
    "created_at": "string", // timestamp, e.g. '2023-02-07 14:56:49.386042'
    "data": {
        "license_id": "string",
        "preds": [
        {
            "image_frame": "string", // base64 string
            "prob": "float",
            "tags": "string[]"
        },
        
        ]
    }
}    


If the prob field in the preds array is less than 0.25, the Producer will append the tag low_prob to the tags list.

The Consumer will process the message and append it to the output.csv file in the data directory. Each item in the preds array will correspond to its own row in the CSV file.

To stop the services, press Ctrl+C or run docker-compose down in another terminal.

the CSV output will save at : consumer container/output/output.csv