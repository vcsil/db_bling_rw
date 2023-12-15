#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
preencher_banco_de_dados.

Script para pegar os dados do Bling e passar para o banco de dados
"""
from preencherModulos.preencher_modulos import preencher_modulos
import logging

# =-=-=-=-=-=-=-=-=-=-=-=-= Preencher Modulo Contatos =-=-=-=-=-=-=-=-=-=-=-=-=


def main():
    """Executa programa."""
    log_texto = '%(asctime)s; %(levelname)s;\t%(name)s;\t'
    log_texto += '%(module)s; - %(funcName)s;'
    log_texto += '\t%(message)s;'

    logging.basicConfig(filename='meu_log.txt', level=logging.DEBUG,
                        format=log_texto, datefmt='%d/%m/%Y %H:%M:%S,%j',
                        filemode='w')

    preencher_modulos()


# Criar uma função para cada atribulo dos dicionários

if __name__ == '__main__':
    main()
