from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return 'Hello 👋'

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    messages = [message.to_dict() for message in Message.query.order_by('created_at').all()]

    if request.method == 'GET':
        return make_response(messages, 200)
    
    elif request.method == 'POST':
        new_message = Message(
            body = request.get_json()['body'],
            username = request.get_json()['username']
        )

        db.session.add(new_message)
        db.session.commit()

        response_body = new_message.to_dict()

        return make_response(response_body, 201)

@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message_by_id = Message.query.filter_by(id=id).first()

    if message_by_id == None:
        response_body = {
            "message": f"Record {id} does not exist in the database. Please try again."
        }
        return make_response(response_body, 404)
    
    if request.method == 'GET':
        message_by_id_dict = message_by_id.to_dict()
        return make_response(message_by_id_dict, 200)

    elif request.method == 'PATCH':
        for attr in request.get_json():
            setattr(message_by_id, attr, request.get_json().get(attr))

        db.session.add(message_by_id)
        db.session.commit()

        response_body = message_by_id.to_dict()

        return make_response(response_body, 200)
    
    elif request.method == 'DELETE':
        db.session.delete(message_by_id)
        db.session.commit()

        response_body = {
            'delete_successful': True,
            'message': 'Successfully deleted message'
        }

        return make_response(response_body, 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
