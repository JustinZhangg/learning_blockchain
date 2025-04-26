import hashlib
import json
from time import time
from textwrap import dedent
from uuid import uuid4
from urllib.parse import urlparse
from flask import Flask, jsonify, request
import requests
from threading import Thread
import os

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transaction = []
        self.node = set()
        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self,proof,previous_hash=None):
        # Creates a new Block and adds it to the chain
        block = {
            'index': len(self.chain)+1,
            'timestamp': time(),
            'transaction': self.current_transaction,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transaction  
        self.current_transaction = []

        self.chain.append(block)
        return block

    def new_transaction(self,sender,recipient,amount):
        # Adds a new transaction to the list of transaction
        self.current_transaction.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

    def register_node(self,address):
        # Adds a new node to the list of node
        parsed_url = urlparse(address)
        self.node.add(parsed_url.netloc)

    def valid_chain(self,chain):
        # Determine if a given blockchain is valid
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False
            if not self.valid_proof(last_block['proof'],block['proof']):
                return False
            last_block = block 
            current_index += 1
        return True
    
    def resolve_conflict(self):
        neighbour = self.node 
        new_chain = None
        # We're only looking for chain longer than our
        max_length = len(self.chain)

        # Grab and verify the chain from all the node in our network  
        for node in neighbour:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = 0
                    new_chain = chain
        # Replace our chain if we discovered a new, valid chain longer than our
        if new_chain:
            self.chain = new_chain
            return True
        return False


    @staticmethod
    def hash(block):
        # Hashes a Block
        block_string = json.dumps(block,sort_key=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # Returns the last Block in the chain
        return self.chain[-1]
    
    def proof_of_work(self,last_proof):
        proof = 0
        while self.valid_proof(last_proof,proof) is False:
            proof += 1
        return proof
    
    @staticmethod
    def valid_proof(last_proof,proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == '0000'

# create two instance of the Blockchain class
# in order to test consensus function
app = Flask(__name__)
app1 = Flask(__name__)

# as flask0.12.4 not compatible with werkzeug>1.0.0
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app1.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
node_identifier = str(uuid4()).replace('-','')
blockchain = Blockchain()
blockchain1 = Blockchain()

@app.route('/mine',method=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof,previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transaction': block['transaction'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response),200

@app.route('/transaction/new',method=['POST'])
def new_transaction():
    # cache=False 参数表示每次调用 request.get_json() 
    # 方法时都重新解析 JSON 数据，而不是使用缓存的结果。
    # 默认情况下，request.get_json() 方法将缓存解析的结果，
    # 以提高性能。
    value = request.get_json(force=True,cache=False)
    required = ['sender', 'recipient', 'amount']
    if not all(k in value for k in required):
        return f'Missing value {value}',400
    index = blockchain.new_transaction(value['sender'],
                                       value['recipient'],
                                       value['amount'])
    response = {'message': f'Transaction will be added to block {index}'}
    return jsonify(response),201

@app.route('/chain',method=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response),200

@app.route('/node/register',method=['POST'])
def register_node():
    value = request.get_json(force=True,cache=False)

    node = value.get('node')
    if node is None:
        return "Error: Please supply a valid list of node",400

    for node in node:
        blockchain.register_node(node)

    response = {
        'message': 'New node have been added',
        'total_node': list(blockchain.node),
    }
    return jsonify(response),201

@app.route('/node/resolve',method=['GET'])
def consensus():
    replaced = blockchain.resolve_conflict()
    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response),200

# thread(target=lambda: app.run(port=5000)).start()


@app1.route('/mine',method=['GET'])
def mine():
    last_block = blockchain1.last_block
    last_proof = last_block['proof']
    proof = blockchain1.proof_of_work(last_proof)

    blockchain1.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    previous_hash = blockchain1.hash(last_block)
    block = blockchain1.new_block(proof,previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transaction': block['transaction'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response),200
@app1.route('/chain',method=['GET'])
def full_chain():
    response = {
        'chain': blockchain1.chain,
        'length': len(blockchain1.chain),
    }
    return jsonify(response),200

if __name__ == '__main__':
    # os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    # thread(target=app).start()
    app.run(debug=True,port=5000)
    app1.run(debug=True,port=5001)
    