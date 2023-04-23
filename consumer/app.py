import os
import csv
import pika
import json
import time



def validate_input_data(data):
    required_keys = {'device_id', 'client_id', 'created_at', 'data'}
    data_keys = data.keys()
    
    if not required_keys.issubset(data_keys):
        return False

    required_data_keys = {'license_id', 'preds'}
    data_keys = data['data'].keys()

    if not required_data_keys.issubset(data_keys):
        return False

    for pred in data['data']['preds']:
        required_pred_keys = {'image_frame', 'prob', 'tags'}
        pred_keys = pred.keys()

        if not required_pred_keys.issubset(pred_keys):
            return False

    return True



def connect_to_rabbitmq(host, retries=10, delay=8):
    for i in range(retries):
        try:
            return pika.BlockingConnection(pika.ConnectionParameters(host=host))
        except pika.exceptions.AMQPConnectionError:
            if i < retries - 1:  # Prevent logging the last attempt as a failure
                print(f"Failed to connect to RabbitMQ. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print('connected')
                raise

connection = connect_to_rabbitmq(host='rabbitmq')

csv_file = 'output/output.csv'
csv_columns = [
    'device_id', 'client_id', 'created_at', 'license_id', 'image_frame',
    'prob', 'tags'
]

def write_to_csv(data):

    if not validate_input_data(data):
        print("Invalid input data")
        return
    
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)

        if not file_exists:
            writer.writeheader()

        for pred in data['data']['preds']:
            row = {
                'device_id': data['device_id'],
                'client_id': data['client_id'],
                'created_at': data['created_at'],
                'license_id': data['data']['license_id'],
                'image_frame': pred['image_frame'],
                'prob': pred['prob'],
                'tags': ','.join(pred['tags'])
            }
            writer.writerow(row)

def consume_callback(ch, method, properties, body):
    data = json.loads(body)
    write_to_csv(data)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='predictions')

channel.basic_consume(queue='predictions', on_message_callback=consume_callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()