# SunPower PVS5x/PVS6 Notes

Listed below are some of the more useful commands I noted when the SunPower 
PVS5x/PVS6 device was being configured.

## Networking

The SunPower PVS5x/6 devices push data to the SunPower cloud, which requires 
at least one of the following:

- hardwired Ethernet connection
- WiFi connection
- PowerLine Communication (PowerLine ethernet)
- cellular service

For each of the local area network connections, outbound Internet access is 
required.

The data from the PVS5x/6 can be polled using an HTTP connection to Installer
interface (LAN1). The device acts as a DHCP server, listening on:

* IP Address: 172.27.153.1
* Subnet: 255.255.255.0
* Gateway: 172.27.153.1

The web server listens on port 80 and 443.

It also runs a DNS server that sets the sunpowerconsole.com domain to its own
 IP address.

### Bridge

To grab the metrics out of the PVS5x/PVS6, you can use a device like a 
Raspberry Pi to bridge the connection, like so:

```
 +--------+
 |  PVS   |
 |      [LAN2] \
 |      [WiFi] +--- to LAN/Internet --->
 |      [PLC]  /
 |        |
 +-[LAN1]-+
      |
      |
 +-[LAN1]-+
 | R Pi   |
 |       [LAN2] \
 |        |     +--- to LAN
 |       [WiFi] /
 +--------+
```  

Where:
* `PVS.LAN1`: Installer Port (172.27.153.1)
* `PVS.LAN2/WiFi`: Customer WAN Port (IP assigned by your network)
* `RPi.LAN1`: Connected directly to PVS.LAN1, will get an IP address assigned
 by the PVS (172.27.153.0/24)
* `RPi.LAN2/WiFi`: IP address assigned by your network

In this setup, the Raspberry Pi is acting as a bridge/proxy to the internal 
PVS network. Setting up a reverse proxy will then allow you to pull data off 
the PVS.

```
[user] --- http call ---> [r-pi] --- proxy http call ---> [pvs]
```

## HTTP API

```http://sunpowerconsole.com/cgi-bin/dl_cgi?Command```

### Commands

* Start

    Starts the configuration session. Returns the result of the command, 
    including information about the Supervisor component:

    ```json
    {
      "result": "succeed",
      "supervisor": {
        "FWVER": "1.0.0",
        "MODEL": "PVS6",
        "SERIAL": "ZT01234567890ABCDE",
        "SWVER": "2019.5, Build 4150"
      }
    }  
    ```  

* Stop

    Stops the configuration session

    ```json
    {
      "result": "succeed"
    }  
    ```  

* Get_Comm

    Returns the list of communication interfaces and network status

    ```json
    {
      "networkstatus": {
        "interfaces": [
          {
            "interface": "wan",
            "internet": "up",
            "ipaddr": "192.168.20.10",
            "link": "connected",
            "mode": "wan",
            "sms": "reachable",
            "state": "up"
          },
          {
            "interface": "plc",
            "internet": "down",
            "ipaddr": "",
            "link": "disconnected",
            "pairing": "unpaired",
            "sms": "unreachable",
            "speed": 0,
            "state": "down"
          },
          {
            "interface": "sta0",
            "internet": "down",
            "ipaddr": "192.168.21.10",
            "signal": "-74",
            "sms": "unreachable",
            "ssid": "Home Network",
            "status": "connected"
          },
          {
            "interface": "cell",
            "internet": "down",
            "ipaddr": "",
            "is_primary": false,
            "link": "disconnected",
            "modem": "MODEM_OK",
            "provider": "UNKNOWN",
            "signal": 0,
            "sim": "SIM_READY",
            "sms": "unreachable",
            "state": "DOWN",
            "status": "NOT_REGISTERED"
          }
        ],
        "system": {
          "interface": "wan",
          "internet": "up",
          "sms": "reachable"
        },
        "ts": "1557210800"
      },
      "result": "succeed"
    }
    ```  

* DeviceList

    Returns the list of discovered devices.
    
    ```json
    {
      "devices": [
        {
          "CURTIME": "2019,05,11,16,53,53",
          "DATATIME": "2019,05,11,16,50,00",
          "DETAIL": "detail",
          "DEVICE_TYPE": "PVS",
          "HWVER": "6.0",
          "MODEL": "PV Supervisor PVS6",
          "SERIAL": "ZT01234567890ABCDEF",
          "STATE": "working",
          "STATEDESCR": "Working",
          "SWVER": "2019.5, Build 4150",
          "dl_comm_err": "270",
          "dl_cpu_load": "0.57",
          "dl_err_count": "0",
          "dl_flash_avail": "86825",
          "dl_mem_used": "41320",
          "dl_scan_time": "0",
          "dl_skipped_scans": "0",
          "dl_untransmitted": "57",
          "dl_uptime": "2181",
          "panid": 1234567890
        },
        {
          "CAL0": "50",
          "CURTIME": "2019,05,11,16,53,53",
          "DATATIME": "2019,05,11,16,53,45",
          "DESCR": "Power Meter PVS6M01234567p",
          "DEVICE_TYPE": "Power Meter",
          "ISDETAIL": true,
          "MODEL": "PVS6M0400p",
          "OPERATION": "noop",
          "PORT": "",
          "SERIAL": "PVS6M01234567p",
          "STATE": "working",
          "STATEDESCR": "Working",
          "SWVER": "3000",
          "TYPE": "PVS5-METER-P",
          "ct_scl_fctr": "50",
          "freq_hz": "60.0859",
          "net_ltea_3phsum_kwh": "198.92",
          "origin": "data_logger",
          "p_3phsum_kw": "1.9867",
          "q_3phsum_kvar": "0.3025",
          "s_3phsum_kva": "2.013",
          "tot_pf_rto": "0.9882"
        },
        {
          "CAL0": "100",
          "CURTIME": "2019,05,11,16,53,53",
          "DATATIME": "2019,05,11,16,53,45",
          "DESCR": "Power Meter PVS6M01234567c",
          "DEVICE_TYPE": "Power Meter",
          "ISDETAIL": true,
          "MODEL": "PVS6M0400c",
          "OPERATION": "noop",
          "PORT": "",
          "SERIAL": "PVS6M01234567c",
          "STATE": "working",
          "STATEDESCR": "Working",
          "SWVER": "3000",
          "TYPE": "PVS5-METER-C",
          "ct_scl_fctr": "100",
          "freq_hz": "60.0859",
          "net_ltea_3phsum_kwh": "-65.65",
          "origin": "data_logger",
          "p_3phsum_kw": "-1.55",
          "q_3phsum_kvar": "-0.8042",
          "s_3phsum_kva": "1.784",
          "tot_pf_rto": "-0.8717"
        },
        {
          "CURTIME": "2019,05,11,16,53,53",
          "DATATIME": "2019,05,11,16,52,00",
          "DESCR": "Inverter E00000000000001",
          "DEVICE_TYPE": "Inverter",
          "ISDETAIL": true,
          "MODEL": "AC_Module_Type_E",
          "MOD_SN": "P07M01234567",
          "NMPLT_SKU": "",
          "OPERATION": "noop",
          "PORT": "",
          "SERIAL": "E00000000000001",
          "STATE": "working",
          "STATEDESCR": "Working",
          "SWVER": "118079776",
          "TYPE": "SOLARBRIDGE",
          "freq_hz": "59.99",
          "i_3phsum_a": "0.51",
          "i_mppt1_a": "2.47",
          "ltea_3phsum_kwh": "13.0464",
          "origin": "data_logger",
          "p_3phsum_kw": "0.125",
          "p_mpptsum_kw": "0.1282",
          "stat_ind": "0",
          "t_htsnk_degc": "29",
          "v_mppt1_v": "51.82",
          "vln_3phavg_v": "245.07"
        },
        {
          "CURTIME": "2019,05,11,16,53,53",
          "DATATIME": "2019,05,11,16,52,00",
          "DESCR": "Inverter E00000000000002",
          "DEVICE_TYPE": "Inverter",
          "ISDETAIL": true,
          "MODEL": "AC_Module_Type_E",
          "MOD_SN": "P07M01234568",
          "NMPLT_SKU": "",
          "OPERATION": "noop",
          "PORT": "",
          "SERIAL": "E00000000000002",
          "STATE": "working",
          "STATEDESCR": "Working",
          "SWVER": "118079776",
          "TYPE": "SOLARBRIDGE",
          "freq_hz": "59.99",
          "i_3phsum_a": "0.51",
          "i_mppt1_a": "2.49",
          "ltea_3phsum_kwh": "13.0527",
          "origin": "data_logger",
          "p_3phsum_kw": "0.1271",
          "p_mpptsum_kw": "0.1304",
          "stat_ind": "0",
          "t_htsnk_degc": "29",
          "v_mppt1_v": "51.94",
          "vln_3phavg_v": "244.82"
        },
        {
          "CURTIME": "2019,05,11,16,53,53",
          "DATATIME": "2019,05,11,16,52,00",
          "DESCR": "Inverter E00000000000003",
          "DEVICE_TYPE": "Inverter",
          "ISDETAIL": true,
          "MODEL": "AC_Module_Type_E",
          "MOD_SN": "P07M01234569",
          "NMPLT_SKU": "",
          "OPERATION": "noop",
          "PORT": "",
          "SERIAL": "E00121852034919",
          "STATE": "working",
          "STATEDESCR": "Working",
          "SWVER": "118079776",
          "TYPE": "SOLARBRIDGE",
          "freq_hz": "59.99",
          "i_3phsum_a": "0.5",
          "i_mppt1_a": "2.46",
          "ltea_3phsum_kwh": "12.7868",
          "origin": "data_logger",
          "p_3phsum_kw": "0.125",
          "p_mpptsum_kw": "0.1282",
          "stat_ind": "0",
          "t_htsnk_degc": "29",
          "v_mppt1_v": "52.11",
          "vln_3phavg_v": "244.64"
        }
      ],
      "result": "succeed"
    }
    ```

* CheckFW

    Returns the URL to new versions of the firmware. Extra parameter `type` 
    with values `residential` or `commercial` is expected.
    
    ```json
    {
      "url": "none"
    }
    ```

### Other Commands

* DeviceDetails

    Extra parameter `SerialNumber` required

* GridProfile
* GridProfileRefresh
* GetCellPurchased
* GetDiscoveryProgress
* SetCellPurchased

## Device Details

I've found the PVS5x/PVS6 returns 3 distinct devices:

- Supervisor
- Power Meter (consumption, production)
- Inverter 

The return payload follows a convention where the properties of a given 
device are in UPPERCASE, whereas metrics/key-performance-indicators (KPIs) are
in lower-case. For example:

These are the properties of the device:
```json
    {
      "CURTIME": "2019,05,14,03,53,46",
      "DATATIME": "2019,05,14,03,50,00",
      "DETAIL": "detail",
      "DEVICE_TYPE": "PVS",
      "HWVER": "6.0",
      "MODEL": "PV Supervisor PVS6",
      "SERIAL": "ZT01234567890ABCDE",
      "STATE": "working",
      "STATEDESCR": "Working",
      "SWVER": "2019.5, Build 4150"
    }
```

These are the metrics/KPIs of the device:
```json
    {
      "dl_comm_err": "300",
      "dl_cpu_load": "0.27",
      "dl_err_count": "0",
      "dl_flash_avail": "76618",
      "dl_mem_used": "38812",
      "dl_scan_time": "0",
      "dl_skipped_scans": "0",
      "dl_untransmitted": "9642",
      "dl_uptime": "12894",
      "panid": 3741506586
    }
```

### Supervisor

The Supervisor component refreshes approximately once every 5 minutes.

Example payload:

```json
    {
      "CURTIME": "2019,05,14,03,53,46",
      "DATATIME": "2019,05,14,03,50,00",
      "DETAIL": "detail",
      "DEVICE_TYPE": "PVS",
      "HWVER": "6.0",
      "MODEL": "PV Supervisor PVS6",
      "SERIAL": "ZT01234567890ABCDE",
      "STATE": "working",
      "STATEDESCR": "Working",
      "SWVER": "2019.5, Build 4150",
      "dl_comm_err": "300",
      "dl_cpu_load": "0.27",
      "dl_err_count": "0",
      "dl_flash_avail": "76618",
      "dl_mem_used": "38812",
      "dl_scan_time": "0",
      "dl_skipped_scans": "0",
      "dl_untransmitted": "9642",
      "dl_uptime": "12894",
      "panid": 1234567890
    }
```

* `dl_comm_err`: (?) Number of comms errors 
* `dl_cpu_load`: (?) 1-minute load average
* `dl_err_count`: (?) Number of errors detected since last report 
* `dl_flash_avail`: amount of free space, in KiB (assumed 1GiB of storage)
* `dl_mem_used`: amount of memory used, in KiB (assumed 1GiB of RAM)
* `dl_scan_time`: (?)
* `dl_skipped_scans`: (?)
* `dl_untransmitted`: (?) Number of untransmitted events/records
* `dl_uptime`: number of seconds the system has been running
* `panid`: (?) 

### Power Meter

The Power Meter device measures either consumption or production -- this 
corresponds to the J3 terminal block for CONS L1/L2 and PROD L3.

The Power Meter data refreshes approximately once every 15 seconds.

Example payload:

```json
    {
      "CAL0": "50",
      "CURTIME": "2019,05,11,16,53,53",
      "DATATIME": "2019,05,11,16,53,45",
      "DESCR": "Power Meter PVS6M01234567p",
      "DEVICE_TYPE": "Power Meter",
      "ISDETAIL": true,
      "MODEL": "PVS6M0400p",
      "OPERATION": "noop",
      "PORT": "",
      "SERIAL": "PVS6M01234567p",
      "STATE": "working",
      "STATEDESCR": "Working",
      "SWVER": "3000",
      "TYPE": "PVS5-METER-P",
      "ct_scl_fctr": "50",
      "freq_hz": "60.0859",
      "net_ltea_3phsum_kwh": "198.92",
      "origin": "data_logger",
      "p_3phsum_kw": "1.9867",
      "q_3phsum_kvar": "0.3025",
      "s_3phsum_kva": "2.013",
      "tot_pf_rto": "0.9882"
    }
```

* `CAL0`: The calibration-reference CT sensor size (50A for production, 100A 
for consumption)
* `ct_scl_fctr`: The CT sensor size (50A for production, 100A/200A for 
consumption)
* `freq_hz`: Operating Frequency
* `net_ltea_3phsum_kwh`: Total Net Energy (kilowatt-hours)
* `p_3phsum_kw`: Average real power (kilowatts)
* `q_3phsum_kvar`: Reactive power (kilovolt-amp-reactive)
* `s_3phsum_kva`: Apparent power (kilovolt-amp)
* `tot_pf_rto`: Power Factor ratio (real power / apparent power)   

### Inverter

The Inverter device reports the data from the SunPower Equinox inverter 
module. Data is refreshed approximately once every 15 seconds *when the 
device is up and running* -- which means when there's sunlight. The device 
may switch to an *error* state, such as when there's heavy shading or at night.

Example payload:

```json
    {
      "CURTIME": "2019,05,11,16,53,53",
      "DATATIME": "2019,05,11,16,52,00",
      "DESCR": "Inverter E00000000000001",
      "DEVICE_TYPE": "Inverter",
      "ISDETAIL": true,
      "MODEL": "AC_Module_Type_E",
      "MOD_SN": "P07M01234567",
      "NMPLT_SKU": "",
      "OPERATION": "noop",
      "PORT": "",
      "SERIAL": "E00000000000001",
      "STATE": "working",
      "STATEDESCR": "Working",
      "SWVER": "118079776",
      "TYPE": "SOLARBRIDGE",
      "freq_hz": "59.99",
      "i_3phsum_a": "0.51",
      "i_mppt1_a": "2.47",
      "ltea_3phsum_kwh": "13.0464",
      "origin": "data_logger",
      "p_3phsum_kw": "0.125",
      "p_mpptsum_kw": "0.1282",
      "stat_ind": "0",
      "t_htsnk_degc": "29",
      "v_mppt1_v": "51.82",
      "vln_3phavg_v": "245.07"
    }
```

When the device is in *working* state, the following metrics are available:

* `freq_hz`: Operating Frequency
* `i_3phsum_a`: AC Current (amperes) 
* `i_mppt1_a`: DC Current (amperes)
* `ltea_3phsum_kwh`: Total energy (kilowatt-hours)
* `p_3phsum_kw`: AC Power (kilowatts)
* `p_mpptsum_kw`: DC Power (kilowatts)
* `t_htsnk_degc`: Heatsink temperature (degrees Celsius)
* `v_mppt1_v`: DC Voltage (volts)
* `vln_3phavg_v`: AC Voltage (volts)  
  
