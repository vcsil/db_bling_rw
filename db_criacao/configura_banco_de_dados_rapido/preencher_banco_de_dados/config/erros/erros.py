#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 19:15:03 2023

@author: vcsil
"""

class UnauthorizedError(Exception):
    def __init__(self, message="Unauthorized access"):
        self.message = message
        super().__init__(self.message)