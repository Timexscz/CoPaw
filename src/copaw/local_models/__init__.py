# -*- coding: utf-8 -*-
# Copyright 2025 The CoPaw Authors
# Copyright 2025-2026 Timexscz (CoPaw-CE Community Edition)
# SPDX-License-Identifier: Apache-2.0
"""Local model management and inference."""

from .schema import (
    BackendType,
    DownloadSource,
    LocalModelInfo,
    DownloadProgress,
)
from .manager import (
    LocalModelManager,
    list_local_models,
    get_local_model,
    delete_local_model,
)
from .factory import (
    create_local_chat_model,
    unload_active_model,
    get_active_local_model,
)

__all__ = [
    "BackendType",
    "DownloadSource",
    "LocalModelInfo",
    "DownloadProgress",
    "LocalModelManager",
    "list_local_models",
    "get_local_model",
    "delete_local_model",
    "create_local_chat_model",
    "unload_active_model",
    "get_active_local_model",
]
