# Learning Blockchain

This is a simple blockchain implementation in Python for educational purposes.

## Features
- Basic blockchain structure with blocks and transactions
- Proof of Work consensus algorithm
- Node registration and network consensus
- REST API for interacting with the blockchain
- Multiple node support for testing consensus

## Requirements
- Python 3.x
- Flask
- requests

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/JustinZhangg/learning_blockchain.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Blockchain
1. Start the first node:
   ```bash
   python blockchain_demo.py
   ```
2. (Optional) Start additional nodes on different ports for testing consensus.

## API Endpoints
- `GET /mine`: Mine a new block
- `POST /transactions/new`: Create a new transaction
- `GET /chain`: Return the full blockchain
- `POST /nodes/register`: Register new nodes
- `GET /nodes/resolve`: Consensus algorithm to resolve conflicts

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
