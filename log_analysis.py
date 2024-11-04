import re
import datetime
import os

ACCESS_LOG = '/var/log/apache/access.log' 
ERROR_LOG = '/var/log/apache/error.log'    

def parse_access_log(log_file):
    traffic_data = {}
    user_agents = {}

   
    access_pattern = re.compile(
        r'(\S+) - - \[(.+?)\] "(\S+) (\S+) \S+" (\d{3}) (\d+) "(.*?)" "(.*?)"'
    )

    with open(log_file, 'r') as f:
        for line in f:
            match = access_pattern.match(line)
            if match:
                ip, timestamp, method, path, status, size, referrer, user_agent = match.groups()
                date_time = datetime.datetime.strptime(timestamp.split()[0], "%d/%b/%Y:%H:%M:%S")
                date_time_str = date_time.strftime("%Y-%m-%d %H:%M:%S")

               
                if path not in traffic_data:
                    traffic_data[path] = {}
                if ip not in traffic_data[path]:
                    traffic_data[path][ip] = {'count': 0, 'user_agents': set()}
                traffic_data[path][ip]['count'] += 1
                traffic_data[path][ip]['user_agents'].add(user_agent)

            
                if user_agent not in user_agents:
                    user_agents[user_agent] = 0
                user_agents[user_agent] += 1

    return traffic_data, user_agents

def parse_error_log(log_file):
    error_data = {}

   
    error_pattern = re.compile(r'^\[([^\]]+)\] \[(\S+)\] \s*(.*)$')

    with open(log_file, 'r') as f:
        for line in f:
            match = error_pattern.match(line)
            if match:
                timestamp, error_type, message = match.groups()
                date_time = datetime.datetime.strptime(timestamp.split()[0], "%Y-%m-%d %H:%M:%S")
                date_time_str = date_time.strftime("%Y-%m-%d %H:%M:%S")

                if message not in error_data:
                    error_data[message] = []
                error_data[message].append((date_time_str, error_type))

    return error_data

def save_traffic_data(traffic_data):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'traffic_{timestamp}.txt'
    with open(filename, 'w') as f:
        for path, accesses in traffic_data.items():
            f.write(f'Page: {path}\n')
            for ip, info in accesses.items():
                f.write(f'  IP: {ip}, Count: {info["count"]}, User Agents: {", ".join(info["user_agents"])}\n')
            f.write('\n')
    print(f'Traffic data saved to {filename}')

def save_error_data(error_data):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'errors_{timestamp}.txt'
    with open(filename, 'w') as f:
        for message, occurrences in error_data.items():
            f.write(f'Error: {message}\n')
            for occurrence in occurrences:
                f.write(f'  Time: {occurrence[0]}, Type: {occurrence[1]}\n')
            f.write('\n')
    print(f'Error data saved to {filename}')

def main():
    traffic_data, user_agents = parse_access_log(ACCESS_LOG)
    error_data = parse_error_log(ERROR_LOG)

    save_traffic_data(traffic_data)
    save_error_data(error_data)

if __name__ == '__main__':
    main()
