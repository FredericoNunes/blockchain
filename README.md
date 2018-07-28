# Oficina BlockChain
## Projeto Original em inglês => Learn Blockchains by Building One

[![Build Status](https://travis-ci.org/dvf/blockchain.svg?branch=master)](https://travis-ci.org/dvf/blockchain)

Código fonte do port em [Building a Blockchain](https://medium.com/p/117428612f46). 

## Instalação

1. Certifique-se [Python 3.6+](https://www.python.org/downloads/) is installed. 
2. Install [pipenv](https://github.com/kennethreitz/pipenv). 

```
$ pip install pipenv 
```

3. Crie um _virtual environment_ (ambiente virtual) e específiquea versão do Python python. 

```
$ pipenv --python=python3.6
```

4. Instalar os requerimentos.  

```
$ pipenv install 
``` 

5. Inciar o Servidor:
    * `$ pipenv run python blockchain.py` 
    * `$ pipenv run python blockchain.py -p 5001`
    * `$ pipenv run python blockchain.py --port 5002`
