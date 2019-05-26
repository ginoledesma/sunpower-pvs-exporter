# -*- coding: utf-8 -*-
"""
pytest collector unit test
"""

import os
import requests_mock


def test_collect(collector):
    """
    unit test: base case
    """
    path = os.path.join(os.path.dirname(__file__),
                        "resources",
                        "device_list.json")

    url = "http://sunpowerconsole.com:80/cgi-bin/dl_cgi?Command=DeviceList"
    with requests_mock.mock() as mocked:
        with open(path) as file_handle:
            mocked.get(url, status_code=200, text=file_handle.read())

        metrics = collector.collect()

        # Spot-check some values: 0.017 kw becomes 17.4w
        assert any(['sunpower_pvs_inverter_ac_power' in str(m) and
                    'value=17.4' in str(m)
                    for m in metrics])


def test_collect_handle_error_state(collector):
    """
    unit test: devices in error state are expected to emit NaN values
    """
    path = os.path.join(os.path.dirname(__file__),
                        "resources",
                        "device_list.error.json")

    url = "http://sunpowerconsole.com:80/cgi-bin/dl_cgi?Command=DeviceList"
    with requests_mock.mock() as mocked:
        with open(path) as file_handle:
            mocked.get(url, status_code=200, text=file_handle.read())

        metrics = collector.collect()

        # Spot-check some values: 0.017 kw becomes 17.4w
        assert any(['sunpower_pvs_inverter_ac_power' in str(m) and
                    'value=nan' in str(m)
                    for m in metrics])
