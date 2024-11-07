# SDN Anomaly Detection System

This project implements an anomaly detection system within a Software-Defined Networking (SDN) environment using Mininet and the Floodlight controller. It detects potential threats by analyzing network flow data based on thresholds for byte rate, connection duration, and connection attempts. The system logs alerts for high byte rate, long-lived connections, and frequent connection attempts.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Setup Instructions](#setup-instructions)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Testing Anomaly Types](#testing-anomaly-types)
7. [Results and Logs](#results-and-logs)
8. [Future Improvements](#future-improvements)
9. [References](#references)

## Project Overview

This project uses:
- **Mininet**: Simulates a virtual network environment for testing.
- **Floodlight Controller**: Manages the SDN flow rules and provides a REST API for retrieving flow data.
- **Python Anomaly Detection Script**: Analyzes network flows to detect anomalies based on predefined thresholds.

The system monitors network traffic to detect and log three primary anomalies:
- High Byte Rate (potentially indicating a DDoS attack)
- Long-Lived Connections
- Frequent Connection Attempts (sign of scanning or reconnaissance)

## Prerequisites

- **Python 3**: Ensure Python 3 is installed.
- **Mininet**: Follow the [Mininet installation guide](http://mininet.org/download/) if it is not already installed.
- **Floodlight Controller**: Install Floodlight and run it as the SDN controller. Download it from [Floodlight GitHub](https://github.com/floodlight/floodlight).
- **Additional Tools**:
  - `iperf`: For generating traffic patterns.
  - `hping3`: For creating multiple connection attempts.

Install additional Python packages:
```bash
pip install requests
```

## Setup Instructions

1. **Start the Floodlight Controller**:
   Keep the controller running throughout the testing process.

2. **Set Up Mininet Topology**:
   Create a Mininet topology with two hosts and one switch, with Floodlight as the remote controller:
   ```bash
   sudo python3 topology.py
   ```

3. **Run xterm for Hosts**:
   Open xterm for each host to easily run commands:
   ```bash
   mininet> xterm h1 h2
   ```

## Configuration

The script relies on a configuration file, `config.json`, to set thresholds for detection. Create or update `config.json` with example thresholds:
```json
{
    "BYTE_RATE_THRESHOLD": 1048576,
    "INTERVAL": 10,
    "PROTOCOL_THRESHOLDS": {
        "HTTP": 500000,
        "DNS": 100000,
        "FTP": 200000,
        "DEFAULT": 1048576
    },
    "MAX_CONNECTION_DURATION": 300,
    "MAX_CONNECTION_ATTEMPTS": 5
}
```

- `BYTE_RATE_THRESHOLD`: Default byte rate limit.
- `INTERVAL`: Frequency (in seconds) for flow checks.
- `PROTOCOL_THRESHOLDS`: Protocol-specific byte rate limits.
- `MAX_CONNECTION_DURATION`: Duration limit for long-lived connections.
- `MAX_CONNECTION_ATTEMPTS`: Connection attempts threshold.

## Usage

1. **Run the Anomaly Detection Script**:
   ```bash
   sudo python3 floodlight_anomaly_detection.py
   ```
   The script fetches flow data from Floodlight’s API, monitors it for anomalies, and logs any detected events.

## Testing Anomaly Types

### High Byte Rate
1. Start `iperf` server on `h2`:
   ```bash
   iperf -s -p 5556
   ```
2. Generate high-byte-rate traffic from `h1`:
   ```bash
   iperf -c 10.0.0.2 -p 5556 -t 10 -b 100M
   ```

### Long-Lived Connections
1. Start `iperf` server on `h2`:
   ```bash
   iperf -s -p 5556
   ```
2. Create a long-duration connection from `h1`:
   ```bash
   iperf -c 10.0.0.2 -p 5556 -t 600
   ```

### Frequent Connection Attempts
1. Using `hping3` on `h1`, send repeated requests to `h2` on various ports:
   ```bash
   hping3 -S 10.0.0.2 -p 80 -c 5
   hping3 -S 10.0.0.2 -p 443 -c 5
   hping3 -S 10.0.0.2 -p 21 -c 5
   hping3 -S 10.0.0.2 -p 22 -c 5
   hping3 -S 10.0.0.2 -p 53 -c 5
   ```
## Results and Logs

Alerts are saved in `anomaly_log.txt`, recording details such as:
- Type of anomaly detected (byte rate, connection duration, connection attempts)
- Switch ID, flow ID, and other metadata for the detected anomaly

**Suggested Visuals**:
- Screenshot of sample log entries for each anomaly type.
- Diagram of the test setup, showing `h1` and `h2` with `iperf` and `hping3` commands.

## Future Improvements

- **Dynamic Thresholds**: Adapt thresholds based on real-time network behavior to minimize false positives.
- **Protocol Classification**: Expand protocol recognition for more accurate anomaly detection.
- **Machine Learning**: Explore integrating machine learning to improve detection accuracy.
- **Automated Response**: Develop automated responses for detected anomalies to isolate suspicious traffic.

## References

1. Floodlight Controller: [GitHub Repository](https://github.com/floodlight/floodlight)
2. Mininet Documentation: [Mininet Guide](http://mininet.org/download/)
