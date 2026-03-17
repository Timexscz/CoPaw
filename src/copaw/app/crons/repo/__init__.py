# -*- coding: utf-8 -*-
# Copyright 2025 The CoPaw Authors
# Copyright 2025-2026 Timexscz (CoPaw-CE Community Edition)
# SPDX-License-Identifier: Apache-2.0
from .base import BaseJobRepository
from .json_repo import JsonJobRepository

__all__ = ["BaseJobRepository", "JsonJobRepository"]
