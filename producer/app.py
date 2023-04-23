from flask import Flask, request, jsonify
import pika
import json





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


def process_data(data):
    if not validate_input_data(data):
        print("Invalid input data")
        return

    for pred in data['data']['preds']:
        if pred['prob'] < 0.25:
            pred['tags'].append('low_prob')

    return data


app = Flask(__name__)

@app.route('/predictions', methods=['POST'])
def predictions():
    data = request.get_json()
    # Process data
    processed_data = process_data(data)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='predictions')

    channel.basic_publish(exchange='', routing_key='predictions', body=json.dumps(processed_data))

    connection.close()

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

    

    