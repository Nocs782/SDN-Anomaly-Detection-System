import requests
import time
import os
import json
import logging

with open('config.json') as config_file:
    config = json.load(config_file)

BYTE_RATE_THRESHOLD = config.get('BYTE_RATE_THRESHOLD')
INTERVAL = config.get('INTERVAL')
PROTOCOL_THRESHOLDS = config.get('PROTOCOL_THRESHOLDS', {})
MAX_CONNECTION_DURATION = config.get('MAX_CONNECTION_DURATION', 300)
MAX_CONNECTION_ATTEMPTS = config.get('MAX_CONNECTION_ATTEMPTS', 5)

API_URL = "http://localhost:8080/wm/core/switch/all/flow/json"
previous_flow_data = {}
connection_attempts = {}

logging.basicConfig(filename='anomaly_log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_flow_stats():
    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(API_URL, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logging.warning("Request timed out. Could not retrieve data from Floodlight.")
            time.sleep(2)
        except requests.exceptions.ConnectionError:
            logging.warning("Could not connect to Floodlight. Please check if the controller is running.")
            time.sleep(2)
        except requests.RequestException as e:
            logging.error(f"Error querying the Floodlight API: {e}")
            return None
    logging.error("Failed to reach Floodlight after multiple attempts.")
    return None

def calculate_byte_rate(flow, previous_flow):
    byte_rate = (int(flow['byte_count']) - int(previous_flow['byte_count'])) / INTERVAL
    return byte_rate

def get_protocol_threshold(port):
    if port == 80:
        return PROTOCOL_THRESHOLDS.get("HTTP", BYTE_RATE_THRESHOLD)
    elif port == 443:
        return PROTOCOL_THRESHOLDS.get("HTTPS", BYTE_RATE_THRESHOLD)
    elif port == 53:
        return PROTOCOL_THRESHOLDS.get("DNS", BYTE_RATE_THRESHOLD)
    elif port == 21:
        return PROTOCOL_THRESHOLDS.get("FTP", BYTE_RATE_THRESHOLD)
    else:
        return PROTOCOL_THRESHOLDS.get("DEFAULT", BYTE_RATE_THRESHOLD)

def detect_long_lived_connections(flow, switch_id):
    duration = int(flow.get('duration_sec', 0))
    if duration > MAX_CONNECTION_DURATION:
        alert_message = (
            f"ALERT: Long-lived connection detected! Switch ID: {switch_id}, "
            f"Flow ID (cookie): {flow.get('cookie')}, Duration: {duration} seconds"
        )
        print(alert_message)
        logging.info(alert_message)

def detect_frequent_connections(flow, switch_id):
    src_ip = flow.get('match', {}).get('ipv4_src')
    dst_ip = flow.get('match', {}).get('ipv4_dst')
    if src_ip and dst_ip:
        if src_ip not in connection_attempts:
            connection_attempts[src_ip] = set()
        connection_attempts[src_ip].add(dst_ip)
        if len(connection_attempts[src_ip]) > MAX_CONNECTION_ATTEMPTS:
            alert_message = (
                f"ALERT: Frequent connections detected! Switch ID: {switch_id}, "
                f"Source IP: {src_ip}, Multiple Destinations"
            )
            print(alert_message)
            logging.info(alert_message)

def detect_anomalies(flow_stats):
    global previous_flow_data

    for switch_id, flow_data in flow_stats.items():
        flows = flow_data.get('flows', [])
        
        for flow in flows:
            flow_id = (switch_id, flow.get('cookie', '0'))
            current_byte_count = int(flow.get('byte_count', 0))
            duration = int(flow.get('duration_sec', 0))
            dst_port = int(flow.get('match', {}).get('tcp_dst', 0))

            protocol_threshold = get_protocol_threshold(dst_port)

            if flow_id in previous_flow_data:
                prev_flow = previous_flow_data[flow_id]
                byte_rate = calculate_byte_rate(flow, prev_flow)
                
                print(f"DEBUG: Flow {flow_id} - Byte Rate: {byte_rate:.2f} bytes/s - Protocol Threshold: {protocol_threshold}")

                if byte_rate > protocol_threshold:
                    alert_message = (
                        f"ALERT: High byte rate detected! Switch ID: {switch_id}, "
                        f"Flow ID (cookie): {flow.get('cookie')}, Duration: {duration} seconds, "
                        f"Byte Rate: {byte_rate:.2f} bytes/s (Threshold: {protocol_threshold})"
                    )
                    print(alert_message)
                    logging.info(alert_message)

            detect_long_lived_connections(flow, switch_id)
            detect_frequent_connections(flow, switch_id)

            previous_flow_data[flow_id] = {
                'byte_count': current_byte_count
            }

if __name__ == "__main__":
    print("Starting anomaly detection...")
    while True:
        os.system('clear')
        flow_stats = get_flow_stats()
        if flow_stats:
            detect_anomalies(flow_stats)
        time.sleep(INTERVAL)
