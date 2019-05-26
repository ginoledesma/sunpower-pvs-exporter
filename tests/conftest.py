# -*- coding: utf-8 -*-
"""
pytest config file
"""

import pytest
try:
    # python 3.x
    from unittest.mock import MagicMock
except ImportError:
    # python 2.7
    from mock import MagicMock

from sunpower_pvs_exporter.exporter import \
    SunPowerPVSupervisorCollector


@pytest.fixture
def collector(monkeypatch):
    """
    Unit test: base case
    """
    col = SunPowerPVSupervisorCollector(use_device_data_timestamp=False)

    attrs = [
        'connect',
        'disconnect',
        'info_metrics',
    ]

    mocked = MagicMock()
    mocked.connect.return_value = []
    mocked.disconnect.return_value = []
    mocked.info_metrics.return_value = []

    for attr in attrs:
        monkeypatch.setattr(col, attr, getattr(mocked, attr))
    return col
