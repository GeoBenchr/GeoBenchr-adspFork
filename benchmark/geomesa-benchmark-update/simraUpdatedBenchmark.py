#!/usr/bin/env python3
import argparse
import threading
import random
import time
import os
import sys
import subprocess
import json
from datetime import datetime, timedelta

##############################################
# Utility Functions
##############################################

def generate_random_position_in_Berlin():
    """Generate a random longitude, latitude pair within Berlin."""
    poslong = random.uniform(13.088346, 13.761160)  # longitude
    poslat  = random.uniform(52.338049, 52.675454)   # latitude
    return poslong, poslat

def generate_random_time_interval(period_start, period_end, duration):
    """
    Generates a random start and end time (ISO8601) within the given period.
    """
    period_start_dt = datetime.strptime(period_start, "%Y-%m-%d %H:%M:%S")
    period_end_dt   = datetime.strptime(period_end, "%Y-%m-%d %H:%M:%S")
    total_duration  = period_end_dt - period_start_dt

    if duration > total_duration:
        raise ValueError("The specified duration exceeds the total period duration.")

    latest_start = period_end_dt - duration
    random_seconds = random.randint(0, int((latest_start - period_start_dt).total_seconds()))
    random_start = period_start_dt + timedelta(seconds=random_seconds)
    random_end   = random_start + duration

    return random_start.strftime("%Y-%m-%dT%H:%M:%SZ"), random_end.strftime("%Y-%m-%dT%H:%M:%SZ")

def get_terraform_output(deployment="multi"):
    """Run terraform output and return parsed JSON output."""
    original_dir = os.getcwd()
    path = os.path.join("../../../geomesa-accumulo/gcp", deployment)
    os.chdir(path)
    result = subprocess.run(['terraform', 'output', '-json'], stdout=subprocess.PIPE)
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print("Error parsing terraform output:", e)
        output = {}
    os.chdir(original_dir)
    return output

##############################################
# Command Execution Helper
##############################################

def execute_cql(query, limit, ssh_cmd_template):
    """
    Replace the placeholder in the ssh command with the query,
    add the limit (if applicable), and run the command.
    """
    final_cmd = ssh_cmd_template.replace('-q ""', f'-q "{query}"')
    if limit != -1:
        final_cmd = final_cmd.replace('-m', f'-m {limit}')
    else:
        final_cmd = final_cmd.replace('-m', "")
    print(f"\nExecuting: {final_cmd}\n")
    start = time.time()
    result = subprocess.run(final_cmd, shell=True, stdout=subprocess.PIPE)
    end = time.time()
    duration = end - start
    with open("durations.csv", "a") as file:
        file.write(f"{query},{limit},{start},{end},{duration}\n")
    print(result.stdout.decode())
    


def execute_query(query_type, limit, ssh_point, ssh_trip):
    try:
        # Use a match-case (Python 3.10+)
        match query_type:
            case "surrounding":
                poslong, poslat = generate_random_position_in_Berlin()
                query = f"DWITHIN(geom, POINT({poslong} {poslat}), 5000, meters)"
                execute_cql(query, limit, ssh_point)

            case "nearest_neighbor":
                poslong, poslat = generate_random_position_in_Berlin()
                query = f"DWITHIN(geom, POINT({poslong} {poslat}), 0.0001, degrees)"
                execute_cql(query, 1, ssh_point)

            case "bounding_box":
                poslong, poslat = generate_random_position_in_Berlin()
                size = 0.1  # degrees
                minx = poslong - size
                miny = poslat - size
                maxx = poslong + size
                maxy = poslat + size
                query = f"BBOX(geom, {minx}, {miny}, {maxx}, {maxy})"
                execute_cql(query, limit, ssh_point)

            case "polygonal_area":
                # Generate a polygon with 4 points (closing the ring)
                lon1, lat1 = generate_random_position_in_Berlin()
                lon2, lat2 = generate_random_position_in_Berlin()
                lon3, lat3 = generate_random_position_in_Berlin()
                lon4, lat4 = generate_random_position_in_Berlin()
                query = f"WITHIN(geom, POLYGON(({lon1} {lat1}, {lon2} {lat2}, {lon3} {lat3}, {lon4} {lat4}, {lon1} {lat1})))"
                execute_cql(query, limit, ssh_point)

            case "ride_traffic":
                # For GeoMesa, we simulate ride traffic by using a static (complex) multiline string.
                ride_id = random.randint(1, 596)
                random_berlin_route = (
                    "MULTILINESTRING(("
                    "13.32246 52.51174, 13.32245 52.51174, 13.32244 52.51174, "
                    "13.32243 52.51174, 13.32242 52.51174, 13.32241 52.51173"
                    "))"
                )
                query = f"INTERSECTS(trip WHERE ride_id = {ride_id}, {random_berlin_route})"
                execute_cql(query, limit, ssh_trip)

            case "intersections":
                poslong_start, poslat_start = generate_random_position_in_Berlin()
                poslong_end, poslat_end = generate_random_position_in_Berlin()
                query = f"INTERSECTS(trip, LINESTRING({poslong_start} {poslat_start}, {poslong_end} {poslat_end}))"
                execute_cql(query, limit, ssh_trip)

            case "trip_intersections":
                #CQL Not possible: joins
                ride_id = random.randint(1, 596)
                query = f"INTERSECTS(trip, LINESTRING({poslong_start} {poslat_start}, {poslong_end} {poslat_end}))"
                execute_cql(query, limit, ssh_trip)

            case "insert_ride":
                
                print("Simulating a single ride insertion...")
                start = time.time()
                # ... perform insertion (omitted) ...
                end = time.time()
                duration = end - start
                with open("durations.csv", "a") as file:
                    file.write(f"insert_ride,1,{start},{end},{duration}\n")
                print("Ride inserted successfully.")

            case "bulk_insert_rides":
                print("Simulating bulk insert rides...")
                rides_inserted = 0
                overall_duration = 0
                while rides_inserted < limit:
                    start = time.time()
                    # ... perform a single ride insertion (omitted) ...
                    end = time.time()
                    overall_duration += (end - start)
                    rides_inserted += 1
                with open("durations.csv", "a") as file:
                    file.write(f"bulk_insert_rides,{limit},{start},{end},{overall_duration}\n")
                print(f"{rides_inserted} rides inserted successfully.")

            case "time_interval":
                # Use a fixed time interval (or generate one)
                start_time, end_time = generate_random_time_interval("2023-07-01 00:00:00", "2023-07-31 23:59:59", timedelta(hours=2))
                query = f"timestamp DURING {start_time}/{end_time}"
                execute_cql(query, limit, ssh_point)

            case "time_slice":
                start_time, end_time = generate_random_time_interval("2023-07-01 00:00:00", "2023-07-31 23:59:59", timedelta(hours=2))
                query = f"timestamp = '{start_time}'"
                execute_cql(query, limit, ssh_point)

            case "get_trip":
                ride_id = random.randint(1, 400)
                query = f"ride_id = {ride_id}"
                execute_cql(query, limit, ssh_trip)

            case "rider_threshold":
                ride_id = random.randint(1, 400)
                query = f"ride_id > {ride_id}"
                execute_cql(query, limit, ssh_trip)

            case "get_trip_length":
                ride_id = random.randint(1, 400)
                query = f"SELECT ride_id, ST_Length(trip) FROM ride_data WHERE ride_id = {ride_id}"
                execute_cql(query, limit, ssh_point)

            case "get_trip_duration":
                ride_id = random.randint(1, 400)
                query = f"SELECT ride_id, MIN(timestamp), MAX(timestamp) FROM ride_data WHERE ride_id = {ride_id}"
                execute_cql(query, limit, ssh_point)

            case "get_trip_speed":
                #CQL Not Possible: ST_Length 
                ride_id = random.randint(1, 400)
                query = f"SELECT ride_id, ST_Length(trip) / (MAX(timestamp) - MIN(timestamp)) AS speed FROM ride_data WHERE ride_id = {ride_id}"
                execute_cql(query, limit, ssh_point)

            case "interval_around_timestamp":
                start_time, end_time = generate_random_time_interval("2023-07-01 00:00:00", "2023-07-31 23:59:59", timedelta(hours=2))
                query = f"timestamp DURING {start_time}-PT30M/{start_time}+PT30M"
                execute_cql(query, limit, ssh_point)

            case "spatiotemporal":
                start_time, end_time = generate_random_time_interval("2023-07-01 00:00:00", "2023-07-31 23:59:59", timedelta(hours=2))
                poslong, poslat = generate_random_position_in_Berlin()
                query = f"timestamp DURING {start_time}/{end_time} AND DWITHIN(geom, POINT({poslong} {poslat}), 5000, meters)"
                execute_cql(query, limit, ssh_point)

            case "count_points_in_time_range":
                start_time, end_time = generate_random_time_interval("2023-07-01 00:00:00", "2023-07-31 23:59:59", timedelta(hours=2))
                query = f"timestamp DURING {start_time}/{end_time}"
                execute_cql(query, limit, ssh_point)

            case "temporal_changes_in_region":
                start_time, end_time = generate_random_time_interval("2023-07-01 00:00:00", "2023-07-31 23:59:59", timedelta(hours=2))
                poslong, poslat = generate_random_position_in_Berlin()
                query = f"timestamp DURING {start_time}/{end_time} AND DWITHIN(geom, POINT({poslong} {poslat}), 5000, meters)"
                execute_cql(query, limit, ssh_point)

            case "peak_activity_times":
                # CQL Not Possible: Aggregations 
                print("Aggregation queries (e.g. peak_activity_times) are not directly supported in GeoMesa via CQL.")

            case "detect_peak_cycling_hours":
                query = "timestamp DURING 2023-07-01T00:00:00Z/2023-07-01T23:59:59Z"
                execute_cql(query, limit, ssh_point)

            case "incident_patterns_by_weekday":
                # CQL Not Possible: aggregations
                print("Aggregation queries (e.g. incident_patterns_by_weekday) are not directly supported in GeoMesa via CQL.")

            case _:
                print(f"Unknown query type: {query_type}")
    except Exception as error:
        print("Error while executing query:", error)
    finally:
        print("Query execution complete.\n")

##############################################
# Thread Runner
##############################################

def run_threads(num_threads, query_type, limit, ssh_point, ssh_trip):
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=execute_query, args=(query_type, limit, ssh_point, ssh_trip))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

##############################################
# Main CLI and Setup
##############################################

def main():
    parser = argparse.ArgumentParser(
        description="GeoMesa Accumulo Benchmarking Script using the SIMRA dataset and CQL queries."
    )
    parser.add_argument("deployment", choices=["single", "multi"],
                        help="Deployment type (single or multi node)")
    parser.add_argument("query_type", help="Type of query to execute (e.g. surrounding, bounding_box, polygonal_area, ride_traffic, etc.)")
    parser.add_argument("--threads", type=int, default=1, help="Number of parallel threads (default: 1)")
    parser.add_argument("--limit", type=int, default=10, help="Limit of records to return (default: 10; use -1 for no limit)")
    args = parser.parse_args()

    # Get terraform output for SSH connection details
    terraform_output = get_terraform_output(args.deployment)
    ssh_user = terraform_output.get("ssh_user", {}).get("value", "your_user")
    if args.deployment == "single":
        ip = terraform_output.get("external_ip_sut_manager", {}).get("value", "127.0.0.1")
    else:
        ip = terraform_output.get("external_ip_sut_namenode_manager", {}).get("value", "127.0.0.1")

    # Build SSH command templates (adjust paths as needed)
    ssh_point = f"ssh {ssh_user}@{ip} '/opt/geomesa-accumulo/bin/geomesa-accumulo export -i test -z localhost -u root -p test -c example -m -q \"\" -f ride_data'"
    ssh_trip  = f"ssh {ssh_user}@{ip} '/opt/geomesa-accumulo/bin/geomesa-accumulo export -i test -z localhost -u root -p test -c example -m -q \"\" -f trip_data'"

    print(f"\n=== GeoMesa Benchmarking Script ===")
    print(f"Deployment: {args.deployment}, Query: {args.query_type}, Threads: {args.threads}, Limit: {args.limit}\n")
    run_threads(args.threads, args.query_type, args.limit, ssh_point, ssh_trip)

if __name__ == "__main__":
    main()
