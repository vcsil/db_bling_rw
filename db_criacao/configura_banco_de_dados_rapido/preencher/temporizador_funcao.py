#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 13:58:54 2024.

@author: vcsil
"""

from datetime import datetime, timedelta
import logging
import pytz
import time

log = logging.getLogger('root')


def agendar_tarefa():
    """15/15min Seg-Sex e Sab 8-14 e 4/4h mos outros horarios."""
    fuso = pytz.timezone("America/Sao_Paulo")
    agora = datetime.now(fuso)
    current_day = agora.weekday()
    current_hour = agora.hour

    if current_day in range(0, 5):  # Segunda a Sexta
        if 8 <= current_hour < 18:  # 8h as 18h - 15min
            t = f"Próxima atualização às: {agora + timedelta(minutes=15)}"
            print(t)
            log.info(t)
            time.sleep(60*15)
        else:
            t = f"Próxima atualização às: {agora + timedelta(hours=4)}"
            print(t)
            log.info(t)
            time.sleep(60*60*4)

    elif current_day == 5:          # Sábado
        if 8 <= current_hour < 14:  # 8h as 14h - 15min
            t = f"Próxima atualização às: {agora + timedelta(minutes=15)}"
            print(t)
            log.info(t)
            time.sleep(60*15)
        else:
            t = f"Próxima atualização às: {agora + timedelta(hours=4)}"
            print(t)
            log.info(t)
            time.sleep(60*60*4)

    else:                           # Domingo (e outros dias)
        t = f"Próxima atualização às: {agora + timedelta(hours=4)}"
        print(t)
        log.info(t)
        time.sleep(60*60*4)         # 4/4h


if __name__ == "__main__":
    pass
