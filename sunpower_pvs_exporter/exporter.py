# -*- coding: utf-8 -*-
"""
SunPower PVS Prometheus Exporter
"""

import logging
import time
from datetime import datetime
from collections import namedtuple

import requests
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.core import CounterMetricFamily
from prometheus_client.core import InfoMetricFamily


DeviceStateLabels = namedtuple("DeviceState", ["device_id",
                                               "device_type",
                                               "model",
                                               "state",
                                               "software_version",
                                               "type",
                                              ])

InverterLabels = namedtuple("Inverter", ["device_id",
                                         "description",
                                         "type",
                                         "model",
                                         "module_id",
                                         "port",
                                         "software_version",
                                        ])

PowerMeterLabels = namedtuple("PowerMeter", ["device_id",
                                             "description",
                                             "type",
                                             "model",
                                             "mode",  # consumption/production
                                             "port",
                                             "ct_rated_current",  # cal0
                                             "software_version",
                                            ])

PVSupervisorLabels = namedtuple("PVS", ["device_id",
                                        "model",
                                        "software_version",
                                       ])


class SunPowerPVSupervisorCollector(object):
    """
    Metrics collector for the SunPower PV Supervisor monitoring device
    Tested against Build 2018.4 - 2019.4
    """
    datetime_pattern = "%Y,%m,%d,%H,%M,%S"

    def __init__(self,
                 hostname="sunpowerconsole.com",
                 port=80,
                 scheme="http",
                 timeout=(5, 5),
                 use_device_data_timestamp=False,
                ):
        self.session = requests.Session()
        self.use_device_data_timestamp = use_device_data_timestamp

        self.timeout = timeout
        self.url = "{scheme}://{hostname}:{port}/cgi-bin/dl_cgi".format(
            scheme=scheme,
            hostname=hostname,
            port=port
        )

    def _get(self, command):
        """
        Convenience function to make a request to the PVS supervisor
        """
        start = datetime.now()
        with self.session.get(self.url,
                              timeout=self.timeout,
                              params={"Command": command}) as response:
            delta = (datetime.now() - start).total_seconds()
            try:
                buf = response.json()
                return buf
            except Exception as err:
                logging.warning("Failed to issue command %s: %s", command, err)
                return dict()
            finally:
                logging.debug("command=%s response_code=%d delta=%0.2f",
                              command, response.status_code, delta)
                logging.debug(response.text)

    @property
    def communication_interfaces(self):
        """
        Return the list of communication interfaces' network status
        """
        return self._get(command="Get_Comm").get("networkstatus", {})

    @property
    def devices(self):
        """
        Return the list of devices
        """
        return self._get(command="DeviceList").get("devices", [])

    @property
    def grid_profile(self):
        """
        Return the status of the Grid Profile setting
        """
        return self._get(command="GridProfileGet")

    def connect(self):
        """
        Start a configuration session with the PVS
        """
        return self._get(command="Start").get("supervisor", {})

    def disconnect(self):
        """
        Stop the configuration session with the PVS
        """
        return self._get(command="Stop")

    @staticmethod
    def from_kilo(value, base=1000):
        """
        Divide the value expressed as kilo by the base
        """
        if value is None:
            return None
        return float(value) * base

    @classmethod
    def from_kibi(cls, value):
        """
        Convert from Kibibytes (KiB) to bytes
        """
        return cls.from_kilo(value, base=1024)

    def inverter_metrics(self):
        """
        Return a list of metrics for the Inverter modules
        """
        labels = InverterLabels._fields

        ac_current = GaugeMetricFamily(
            name="sunpower_pvs_inverter_ac_current",
            documentation="AC Current",
            labels=labels,
            unit="amperes",
        )
        ac_power = GaugeMetricFamily(
            name="sunpower_pvs_inverter_ac_power",
            documentation="AC Power",
            labels=labels,
            unit="watts",
        )
        ac_voltage = GaugeMetricFamily(
            name="sunpower_pvs_inverter_ac_voltage",
            documentation="AC Voltage",
            labels=labels,
            unit="volts",
        )
        dc_current = GaugeMetricFamily(
            name="sunpower_pvs_inverter_dc_current",
            documentation="DC Current",
            labels=labels,
            unit="amperes",
        )
        dc_power = GaugeMetricFamily(
            name="sunpower_pvs_inverter_dc_power",
            documentation="DC Power",
            labels=labels,
            unit="watts",
        )
        dc_voltage = GaugeMetricFamily(
            name="sunpower_pvs_inverter_dc_voltage",
            documentation="DC Voltage",
            labels=labels,
            unit="volts",
        )
        frequency = GaugeMetricFamily(
            name="sunpower_pvs_inverter_operating_frequency",
            documentation="Operating Frequency (hertz)",
            labels=labels,
            unit="hertz",
        )
        energy = GaugeMetricFamily(
            name="sunpower_pvs_inverter_energy_total_watt_hours",
            documentation="Total Energy",
            labels=labels,
            unit="watt_hours",
        )
        heatsink_temp = GaugeMetricFamily(
            name="sunpower_pvs_inverter_heatsink_temperature",
            documentation="Heatsink Temperature",
            labels=labels,
            unit="celcius",
        )

        return [
            dict(key="i_3phsum_a", metric=ac_current),
            dict(key="p_3phsum_kw", metric=ac_power, op=self.from_kilo),
            dict(key="vln_3phavg_v", metric=ac_voltage),

            dict(key="i_mppt1_a", metric=dc_current),
            dict(key="p_mpptsum_kw", metric=dc_power, op=self.from_kilo),
            dict(key="v_mppt1_v", metric=dc_voltage),

            dict(key="freq_hz", metric=frequency),
            dict(key="ltea_3phsum_kwh", metric=energy, op=self.from_kilo),
            dict(key="t_htsnk_degc", metric=heatsink_temp),
        ]

    def power_meter_metrics(self):
        """
        Return a list of metrics for the Power Meter modules
        """
        labels = PowerMeterLabels._fields

        ct_rated_current = GaugeMetricFamily(
            name="sunpower_pvs_power_meter_ct_rated_current",
            documentation="CT Rated Current",
            labels=labels,
            unit="amperes",
        )
        real_power = GaugeMetricFamily(
            name="sunpower_pvs_power_meter_average_real_power",
            documentation="Average real power",
            labels=labels,
            unit="watts",
        )
        reactive_power = GaugeMetricFamily(
            name="sunpower_pvs_power_meter_average_reactive_power",
            documentation="Average reactive power",
            labels=labels,
            unit="volt_amperes_reactive",
        )
        apparent_power = GaugeMetricFamily(
            name="sunpower_pvs_power_meter_average_apparent_power",
            documentation="Average reactive power",
            labels=labels,
            unit="volt_amperes_reactive"
        )
        power_factor = GaugeMetricFamily(
            name="sunpower_pvs_power_meter_power_factor_real_power_per_apparent_power",
            documentation="Power Factor (Real Power / Apparent Power) ratio",
            labels=labels,
        )
        frequency = GaugeMetricFamily(
            name="sunpower_pvs_power_meter_ac_frequency",
            documentation="AC Frequency",
            labels=labels,
            unit="hertz",
        )
        energy_total = GaugeMetricFamily(
            name="sunpower_pvs_power_meter_net_energy",
            documentation="Total Net Energy",
            labels=labels,
            unit="watt_hours",
        )

        return [
            dict(key="ct_scl_fctr", metric=ct_rated_current),
            dict(key="freq_hz", metric=frequency),
            dict(key="net_ltea_3phsum_kwh", metric=energy_total,
                 op=self.from_kilo),
            dict(key="p_3phsum_kw", metric=real_power, op=self.from_kilo),
            dict(key="q_3phsum_kvar", metric=reactive_power, op=self.from_kilo),
            dict(key="s_3phsum_kva", metric=apparent_power, op=self.from_kilo),
            dict(key="tot_pf_rto", metric=power_factor),
        ]

    def supervisor_metrics(self):
        """
        Return a list of metrics for the Supervisor modules
        """
        labels = PVSupervisorLabels._fields

        comm_err = CounterMetricFamily(
            name="sunpower_pvs_supervisor_communication_errors",
            documentation="Total number of communication errors",
            labels=labels,
            unit="",  # counters auto-append _total,
        )
        cpu_load = GaugeMetricFamily(
            name="sunpower_pvs_supervisor_cpu_loadavg",
            documentation="CPU Load Average",
            labels=labels)
        error_count = CounterMetricFamily(
            name="sunpower_pvs_supervisor_errors",
            documentation="Total number of errors",
            labels=labels,
            unit="",  # counters auto-append _total
        )
        flash_available = GaugeMetricFamily(
            name="sunpower_pvs_supervisor_flash_storage_available",
            documentation="Storage available space (bytes)",
            labels=labels,
            unit="bytes",
        )
        mem_used = GaugeMetricFamily(
            name="sunpower_pvs_supervisor_mem_used",
            documentation="Memory used (bytes)",
            labels=labels,
            unit="bytes",
        )
        scan_time = GaugeMetricFamily(
            name="sunpower_pvs_supervisor_scan_time_seconds",
            documentation="Scan time",
            labels=labels,
            unit="seconds",
        )
        skipped_scans = CounterMetricFamily(
            name="sunpower_pvs_supervisor_skipped_scans",
            documentation="Skipped scans",
            labels=labels,
            unit="",  # counters auto-append _total
        )
        untransmitted = CounterMetricFamily(
            name="sunpower_pvs_supervisor_untransmitted_events",
            documentation="Untransmitted events",
            labels=labels,
            unit="",  # counters auto-append _total
        )
        uptime = CounterMetricFamily(
            name="sunpower_pvs_supervisor_uptime_seconds",
            documentation="Uptime (seconds)",
            labels=labels,
            unit="",  # counters auto-append _total
        )

        return [
            dict(key="dl_comm_err", metric=comm_err),
            dict(key="dl_cpu_load", metric=cpu_load),
            dict(key="dl_err_count", metric=error_count),
            dict(key="dl_flash_avail", metric=flash_available,
                 op=self.from_kibi),
            dict(key="dl_mem_used", metric=mem_used,
                 op=self.from_kibi),
            dict(key="dl_scan_time", metric=scan_time),
            dict(key="dl_skipped_scans", metric=skipped_scans),
            dict(key="dl_untransmitted", metric=untransmitted),
            dict(key="dl_uptime", metric=uptime),
        ]

    def info_metrics(self):
        """
        Return a list of information tags for the PV Supervisor
        """
        network_status = self.communication_interfaces
        interface_info = InfoMetricFamily(
            name="sunpower_pvs_communication_interface",
            documentation="Communications Interface Information",
        )

        for comm in network_status.get("interfaces", []):
            value = dict(interface=comm["interface"],
                         internet=comm["internet"],
                         sms=comm["sms"],
                        )
            interface_info.add_metric(labels=[], value=value)

        grid_profile = self.grid_profile
        value = None
        if grid_profile:
            value = dict(id=grid_profile["active_id"],
                         name=grid_profile["active_name"],
                         percent=str(grid_profile["percent"]),
                         status=grid_profile["status"],
                        )
        grid_info = InfoMetricFamily(
            name="sunpower_pvs_grid_profile",
            documentation="Grid Profile",
            value=value,
        )

        return [dict(key="interface_info", metric=interface_info),
                dict(key="grid_profile", metric=grid_info)
               ]

    # pylint: disable=R0201
    def device_state_metrics(self):
        """
        Return a list of metrics for the state of each device
        :return:
        """
        state_metric = GaugeMetricFamily(
            name="sunpower_pvs_device_state",
            documentation="Device (Component/Module) State",
            labels=DeviceStateLabels._fields,
        )
        return [
            dict(key="state", metric=state_metric),
        ]

    def collect(self):
        """
        Query the SunPower PV Supervisor on every exposition
        """
        self.connect()

        info_metrics = self.info_metrics()
        supervisor_metrics = self.supervisor_metrics()
        pm_metrics = self.power_meter_metrics()
        inverter_metrics = self.inverter_metrics()
        device_state_metrics = self.device_state_metrics()

        # Get the metrics for each device
        for device in self.devices:
            label = ""
            metrics = []

            # PV Supervisor
            if device["DEVICE_TYPE"] == "PVS":
                label = PVSupervisorLabels(
                    device_id=device["SERIAL"],
                    model=device["MODEL"],
                    software_version=device["SWVER"],
                )
                metrics = supervisor_metrics

            # Power Meters (production and consumption)
            elif device["DEVICE_TYPE"] == "Power Meter":
                if device["TYPE"].endswith("METER-P"):
                    mode = "production"
                elif device["TYPE"].endswith("METER-C"):
                    mode = "consumption"
                else:
                    mode = "unknown"

                # Current Transformer rated amps
                rated_current = device.get("CAL0", '')

                label = PowerMeterLabels(
                    device_id=device["SERIAL"],
                    description=device["DESCR"],
                    type=device["TYPE"],
                    model=device["MODEL"],
                    mode=mode,
                    port=device["PORT"],
                    ct_rated_current=rated_current,
                    software_version=device["SWVER"],
                )
                metrics = pm_metrics

            # Inverter
            elif device["DEVICE_TYPE"] == "Inverter":
                label = InverterLabels(
                    device_id=device["SERIAL"],
                    description=device["DESCR"],
                    type=device["TYPE"],
                    model=device["MODEL"],
                    module_id=device["MOD_SN"],
                    port=device["PORT"],
                    software_version=device["SWVER"],
                )
                metrics = inverter_metrics

            timestamp = None
            if self.use_device_data_timestamp:
                try:
                    pattern = "%Y,%m,%d,%H,%M,%S"
                    dt = datetime.strptime(device["DATATIME"], pattern)
                    timestamp = time.mktime(dt.timetuple())
                except KeyError:
                    timestamp = None

            for m in metrics:
                op = m.get("op") or float

                # Devices in an "error" state may not have the metrics keys
                value = device.get(m["key"])
                if value is not None:
                    value = op(value)
                else:
                    value = float('nan')

                metric = m["metric"]
                metric.add_metric(labels=label,
                                  value=value,
                                  timestamp=timestamp)

            for m in device_state_metrics:
                labels = DeviceStateLabels(
                    device_id=device["SERIAL"],
                    device_type=device["DEVICE_TYPE"],
                    model=device["MODEL"],
                    software_version=device.get("SWVER", ''),
                    state=device["STATE"],
                    type=device.get("TYPE", ''),
                )
                metric = m["metric"]
                value = 1 if device["STATE"] == "working" else 0
                metric.add_metric(labels=labels,
                                  value=value,
                                  timestamp=timestamp,
                                 )

        for m in info_metrics + \
                 supervisor_metrics + \
                 pm_metrics + \
                 inverter_metrics + \
                 device_state_metrics:
            yield m["metric"]

        # Disconnect
        self.disconnect()
