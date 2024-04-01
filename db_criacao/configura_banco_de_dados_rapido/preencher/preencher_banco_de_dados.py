#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
preencher_banco_de_dados.

Script para pegar os dados do Bling e passar para o banco de dados
"""
from preencherModulos.preencher_modulos import preencher_modulos
import atualizar_banco_de_dados

from logging.handlers import RotatingFileHandler
from datetime import datetime
from pytz import timezone
from tqdm import tqdm
import logging
import time

# =-=-=-=-=-=-=-=-=-=-=-=-= Preencher Modulo Contatos =-=-=-=-=-=-=-=-=-=-=-=-=


def main():
    """Executa programa."""
    log_texto = '%(asctime)s; %(levelname)s;\t%(name)s;\t'
    log_texto += '%(module)s; - %(funcName)s;'
    log_texto += '\t%(message)s;'

    formatter = logging.Formatter(log_texto, datefmt='%d/%m/%Y %H:%M:%S,%j')
    # Configura o fuso horário
    formatter.converter = lambda *args: datetime.now(
        tz=timezone('America/Sao_Paulo')).timetuple()
    # Criando o RotatingFileHandler com tamanho máximo 2MB
    handler = RotatingFileHandler('meu_log_preencher.txt', backupCount=2,
                                  maxBytes=2*1024*1024)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)

    # Obtendo o logger e adicionando o handler
    logger = logging.getLogger("root")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    for sec in tqdm(range(99), desc="Esperando configurações do postgres"):
        time.sleep(1)
        print(sec)

    preencher_modulos()

    atualizar_banco_de_dados.main()


# Criar uma função para cada atribulo dos dicionários

if __name__ == '__main__':
    main()
