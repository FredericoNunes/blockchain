import hashlib
import json
from time import time
from urllib.parse import urlparse
import requests


class Blockchain:
    def __init__(self):
        self.transacao_atual = []
        self.corrente = []
        self.nodes = set()

        # Criar o Bloco genesis
        self.novo_bloco(hash_anterior='1', prova=100)

    def registrar_node(self, endereco):
        """
        Adiciona um novo endereço a lista de Nodes
        :param endereço: endereço do node. Ex. 'http://192.168.0.5:5000'
        """

        parsed_url = urlparse(endereco)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Isso é para aceitar url alem de IP como '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('URL invalida')

    def corrente_valida(self, corrente):
        """
        Determina se um dado Bloco é válido
        :param corrente: um blockchain
        :return: True se valido, False se não
        """

        ultimo_bloco = corrente[0]
        indice_atual = 1

        while indice_atual < len(corrente):
            bloco = corrente[indice_atual]
            print(f'{ultimo_bloco}')
            print(f'{bloco}')
            print("\n-----------\n")
            # verifica de a hash do Bloco é correta
            hash_ultimo_bloco = self.hash(ultimo_bloco)
            if bloco['hash_anterior'] != hash_ultimo_bloco:
                return False

            # verifica se o proof_of_work é correto
            if not self.prova_valida(ultimo_bloco['prova'], bloco['prova'], hash_ultimo_bloco):
                return False

            ultimo_bloco = bloco
            indice_atual += 1

        return True

    def resolver_conflitos(self):
        """
        Esse é o nosso algoritimo de consenso que altera a nossa
        corrente com a maior da rede
        :return: True se for alterado, False se não
        """

        vizinhos = self.nodes
        nova_corrente = None

        # Estamos procurando uma corrente maior que a nossa na rede
        tamanho_max = len(self.corrente)

        # Pegar e verificar cada corrente da rede
        for node in vizinhos:
            resposta = requests.get(f'http://{node}/corrente')

            if resposta.status_code == 200:
                tamanho = resposta.json()['quantidade de ']
                corrente = resposta.json()['corrente']

                # Verifica se a corrente é a maior e se é valida
                if tamanho > tamanho_max and self.corrente_valida(corrente):
                    tamanho_max = tamanho
                    nova_corrente = corrente

        # Substituir nossa corrente se descobrirmos uma maior que a nossa
        if nova_corrente:
            self.corrente = nova_corrente
            return True

        return False

    def novo_bloco(self, prova, hash_anterior):
        """
        Cria um novo Bloco no nosso BlockChain
        :param prova: Prova dada pelo algoritimo de prova de trabalho
        :param hash_anterior: hash do bloco anterior
        :return: Novo Bloco
        """

        bloco = {
            'indice': len(self.corrente) + 1,
            'timestamp': time(),
            'transacoes': self.transacao_atual,
            'prova': prova,
            'hash_anterior': hash_anterior or self.hash(self.corrente[-1]),
        }

        # Limpa a lista de transações atuais
        self.transacao_atual = []

        self.corrente.append(bloco)
        return bloco

    def nova_transacao(self, dono_anterior, dono_atual, quantidade):
        """
        cria uma nova nova transacao para
        ser inserida no novo bloco minerado
        :param dono_anterior: Endereço do dono_anterior
        :param dono_atual: Endereço do dono_atual
        :param quantidade: Quantidade
        :return: O indice do bloco que guardará essa transação
        """
        self.transacao_atual.append({
            'dono_anterior': dono_anterior,
            'dono_atual': dono_atual,
            'quantidade': quantidade,
        })

        return self.ultimo_bloco['indice'] + 1

    @property
    def ultimo_bloco(self):
        return self.corrente[-1]

    @staticmethod
    def hash(bloco):
        """
        Cria uma hash sha-256 para o bloco
        :param bloco: Bloco
        """

        # O dicionario tem que estar ordenado se não haverá incosistencia
        bloco_string = json.dumps(bloco, sort_keys=True).encode()
        return hashlib.sha256(bloco_string).hexdigest()

    def proof_of_work(self, ultimo_bloco):
        """
        Simples algoritimo de prova de Trabalho:
         - Ache um número p' tal que hash(pp') contem 4 zeros do na ponta direita do resultado
         - Onde p é a prova anterior, e p' é a nova prova

        :param ultimo_bloco: <dict> ultimo bloco
        :return: <int>
        """

        ultima_prova = ultimo_bloco['prova']
        ultima_hash = self.hash(ultimo_bloco)

        prova = 0
        while self.prova_valida(ultima_prova, prova, ultima_hash) is False:
            prova += 1

        return prova

    @staticmethod
    def prova_valida(ultima_prova, prova, ultima_hash):
        """
        Validar a Prova de trabalho
        :param ultima_prova: <int> Prova Anterior
        :param prova: <int> Prova Atual
        :param ultima_hash: <str> A hash do bloco anterior
        :return: <bool> True se correto, False se not.
        """

        chute = f'{ultima_prova}{prova}{ultima_hash}'.encode()
        chute_hash = hashlib.sha256(chute).hexdigest()
        return chute_hash[:4] == "0000"
