#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 14:14:32 2024.

@author: vcsil
"""
from atualizarModulos.atualizar_modulos import atualizar_modulos
from logging.handlers import RotatingFileHandler
import logging


def main():
    """Executa programa."""
    log_texto = '%(asctime)s; %(levelname)s;\t%(name)s;\t'
    log_texto += '%(module)s; - %(funcName)s;'
    log_texto += '\t%(message)s;'

    # Criando o RotatingFileHandler com tamanho máximo 2MB e mantendo até 3 arq
    handler = RotatingFileHandler('meu_log_atualizar.txt', maxBytes=2e6)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(log_texto, datefmt='%d/%m/%Y %H:%M:%S,%j')
    handler.setFormatter(formatter)

    # Obtendo o logger e adicionando o handler
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    atualizar_modulos()


if __name__ == "__main__":
    main()
