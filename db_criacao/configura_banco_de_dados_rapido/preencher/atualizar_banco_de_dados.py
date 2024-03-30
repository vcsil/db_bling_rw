#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 14:14:32 2024.

@author: vcsil
"""
from atualizarModulos.atualizar_modulos import atualizar_modulos
from temporizador_funcao import agendar_tarefa

from logging.handlers import RotatingFileHandler
import logging


def main():
    """Executa programa."""
    log_texto = '%(asctime)s; %(levelname)s;\t%(name)s;\t'
    log_texto += '%(module)s; - %(funcName)s;'
    log_texto += '\t%(message)s;'

    formatter = logging.Formatter(log_texto, datefmt='%d/%m/%Y %H:%M:%S,%j')
    # Criando o RotatingFileHandler com tamanho máximo 2MB
    handler = RotatingFileHandler('meu_log_atualizar.txt', backupCount=2,
                                  maxBytes=2*1024*1024)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)

    # Obtendo o logger e adicionando o handler
    logger = logging.getLogger("root")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    atualiza = True
    while atualiza:
        try:
            agendar_tarefa(atualizar_modulos)
        except Exception as e:
            print(e)
            atualiza = False


if __name__ == "__main__":
    main()
