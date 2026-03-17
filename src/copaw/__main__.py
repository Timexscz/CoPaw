# -*- coding: utf-8 -*-
# Copyright 2025 The CoPaw Authors
# Copyright 2025-2026 Timexscz (CoPaw-CE Community Edition)
# SPDX-License-Identifier: Apache-2.0
"""Allow running CoPaw via ``python -m copaw``."""
from .cli.main import cli

if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
