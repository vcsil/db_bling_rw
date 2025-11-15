#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  8 15:37:42 2025

@author: vcsil
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from src.app.core.settings import get_settings

settings = get_settings()

TZ_APP = ZoneInfo(settings.timezone_app)
TZ_BUSINESS = ZoneInfo(settings.timezone_business)

def time_now() -> datetime:
    return datetime.now(timezone.utc)

def time_to_utc(dt):
    if dt.tzinfo is None:
        raise ValueError("datetime naïve: forneça tzinfo")
    return dt.astimezone(timezone.utc)

def time_to_business(dt):
    if dt.tzinfo is None:
        raise ValueError("datetime naïve: forneça tzinfo")
    return dt.astimezone(TZ_BUSINESS)

def iso_z(dt):
    return time_to_utc(dt).isoformat().replace("+00:00", "Z")
