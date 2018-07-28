from uuid import uuid4
from flask import Flask, jsonify, request

from BlockChain import Blockchain


# Instancia o Node
app = Flask(__name__)


# Gerar um endereço global e único para o node
node_identificador = str(uuid4()).replace('-', '')

# Instancia o Blockchain
blockchain = Blockchain()


@app.route('/minerar', methods=['GET'])
def minerar():
    # Executamos o algoritimo de prova de trabalho para pegar a proxima prova
    ultimo_bloco = blockchain.ultimo_bloco
    prova = blockchain.proof_of_work(ultimo_bloco)

    # Temos que ser recompensados por achar a resposta.
    # O dono_anterior é '0' para informar que esse node minerou uma nova moeda de recompensa.
    blockchain.nova_transacao(
        dono_anterior="0",
        dono_atual=node_identificador,
        quantidade=1,
    )

    # Cria um novo bloco e o adiciona a corrente
    hash_anterior = blockchain.hash(ultimo_bloco)
    bloco = blockchain.novo_bloco(prova,hash_anterior)

    resposta = {
        'mensagem': "Novo Bloco Criado",
        'indice': bloco['indice'],
        'transacoes': bloco['transacoes'],
        'prova': bloco['prova'],
        'hash_anteriror': bloco['hash_anterior'],
    }
    return jsonify(resposta), 200


@app.route('/transacoes/nova', methods=['POST'])
def nova_transacao():
    valores = request.get_json()

    # Verificar se os campos estão nos dados POST'ados
    requisitos = ['dono_anterior', 'dono_atual', 'quantidade']
    if not all(k in valores for k in requisitos):
        return 'Faltando Valores', 400

    # Cria uma nova transação
    indice = blockchain.nova_transacao(valores['dono_anterior'], valores['dono_atual'], valores['quantidade'])

    resposta = {'mensagem': f'A transação será adicionado ao {indice}'}
    return jsonify(resposta), 201


@app.route('/corrente', methods=['GET'])
def corrente_inteira():
    resposta = {
        'corrente': blockchain.corrente,
        'quantidade de Blocos': len(blockchain.corrente),
    }
    return jsonify(resposta), 200


@app.route('/nodes/registrar', methods=['POST'])
def registrar_nodes():
    valores = request.get_json()

    nodes = valores.get('nodes')
    if nodes is None:
        return "Erro: Por Favor indique uma lista valida de nodes", 400

    for node in nodes:
        blockchain.registrar_node(node)

    resposta = {
        'mensagem': 'Novo node foi adicionado',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(resposta), 201


@app.route('/nodes/resolver', methods=['GET'])
def consenso():
    substituidos = blockchain.resolver_conflitos()

    if substituidos:
        resposta = {
            'mensagem': 'Nossa Corrente foi Substituida',
            'nova_corrente': blockchain.corrente
        }
    else:
        response = {
            'mensagem': 'Nossa Corrente é a Mandataria',
            'Corrente': blockchain.corrente
        }

    return jsonify(resposta), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5001, type=int, help='porta a ser escutada')
    args = parser.parse_args()
    port = args.port

app.run(host='0.0.0.0', port=port)