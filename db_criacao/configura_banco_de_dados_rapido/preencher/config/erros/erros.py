#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 19:15:03 2023

@author: vcsil
"""


class UnauthorizedError(Exception):
    """Erro de autorização."""

    def __init__(self, message="Unauthorized access"):
        self.message = message
        super().__init__(self.message)


class EsqueceuPassarID(Exception):
    """Esquecer de passar a coluna de ID."""

    def __init__(self, message="Esqueceu de passar a coluna de ID"):
        self.message = message
        super().__init__(self.message)
