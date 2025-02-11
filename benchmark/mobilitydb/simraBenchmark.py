import psycopg2
import threading
import random
import time
import os
import csv
import threading
import sys
import random
from datetime import datetime, timedelta

# Configuration
hostname = sys.argv[1]
portnum = sys.argv[2]
deployment = "multi" if len(sys.argv) < 4 else sys.argv[3]
default_query = "SELECT * FROM cycling_data"

#Timeframe for spatiotemporal queries
period_start = "2023-07-01 00:00:00"
period_end = "2023-07-31 23:59:59"
duration = timedelta(hours=2)

####################### Database utility #######################

# Clear a table
def clear_table(table_name):
    connection = None
    try:
        connection = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="test",
            host=hostname,
            port=portnum
        )
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM {table_name};")
        connection.commit()
        print(f"Table '{table_name}' cleared successfully.")
    except (Exception, psycopg2.Error) as error:
        print(f"Error while clearing table '{table_name}':", error)
    finally:
        if connection:
            connection.close()
            print("PostgreSQL connection is closed.")

# Get maximum ride_id from cycling_data
def get_max_ride_id():
    connection = None
    try:
        connection = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="test",
            host=hostname,
            port=portnum
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT MAX(ride_id) FROM cycling_data;")
            max_ride_id = cursor.fetchone()[0]
        return max_ride_id or 0  # Default to 0 if no records exist
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching max ride_id:", error)
        return 0
    finally:
        if connection:
            connection.close()
            print("PostgreSQL connection is closed.")

# Initial data insertion
def initial_insert():
    def insert_csv_data(file_path, table_name, query_template):
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                query = query_template.format(*row)
                cursor.execute(query)

    connection = None
    try:
        connection = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="test",
            host=hostname,
            port=portnum
        )
        with connection.cursor() as cursor:
            # Insert cycling_data
            for i in range(1, 8):
                file_path = f"../../data/merged0{i}.csv"
                query_template = """
                    INSERT INTO cycling_data(ride_id, rider_id, latitude, longitude, x, y, z, timestamp, point_geom, line_geom)
                    VALUES ({}, {}, {}, {}, {}, {}, {}, '{}',
                            ST_SetSRID(ST_MakePoint({}, {}), 4326),
                            ST_MakeLine(ST_SetSRID(ST_MakePoint({}, {}), 4326), ST_SetSRID(ST_MakePoint({}, {}), 4326)));
                """
                insert_csv_data(file_path, "cycling_data", query_template)

            # Insert cycling_trips
            for i in range(1, 8):
                file_path = f"../../data/trips{i}.csv"
                query_template = """
                    INSERT INTO cycling_trips(ride_id, rider_id, trip)
                    VALUES ({}, {}, {});
                """
                insert_csv_data(file_path, "cycling_trips", query_template)
        connection.commit()
        print("Initial data inserted successfully.")
    except (Exception, psycopg2.Error) as error:
        print("Error during initial data insertion:", error)
    finally:
        if connection:
            connection.close()
            print("PostgreSQL connection is closed.")


# Utility: Generate random position in Berlin
def generate_random_position_in_Berlin():
    return (
        random.uniform(13.088346, 13.761160),  # Longitude
        random.uniform(52.338049, 52.675454)   # Latitude
    )

def generate_random_time_interval(period_start, period_end, duration):
    """
    Generates a random start and end time within a specified period and duration.

    :param period_start: Start of the period as a string in 'YYYY-MM-DD HH:MM:SS' format.
    :param period_end: End of the period as a string in 'YYYY-MM-DD HH:MM:SS' format.
    :param duration: Duration of the interval as a timedelta object.
    :return: Tuple containing start and end times as strings in 'YYYY-MM-DD HH:MM:SS' format.
    """

    period_start_dt = datetime.strptime(period_start, "%Y-%m-%d %H:%M:%S")
    period_end_dt = datetime.strptime(period_end, "%Y-%m-%d %H:%M:%S")
    total_period_duration = period_end_dt - period_start_dt

    if duration > total_period_duration:
        raise ValueError("The specified duration exceeds the total period duration.")

    #calculate start_time and end_time
    latest_start_time = period_end_dt - duration
    random_seconds = random.randint(0, int((latest_start_time - period_start_dt).total_seconds()))
    random_start_time = period_start_dt + timedelta(seconds=random_seconds)

    random_end_time = random_start_time + duration

    # Formatting
    start_time = random_start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time = random_end_time.strftime("%Y-%m-%d %H:%M:%S")

    return start_time, end_time

def get_max_ride_id():
    try:
        connection = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="test",
            host=hostname,
            port=portnum
        )
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(ride_id) FROM cycling_data;")
        records = cursor.fetchall()
        return records[0][0]
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()

def execute_and_log_query(connection, base_query, query_addition, query_type, limit):
    """Helper function to execute a query and log its duration."""
    cursor = connection.cursor()
    full_query = base_query + query_addition
    print(full_query)
    start = time.time()
    cursor.execute(full_query)
    end = time.time()
    duration = end - start
    with open("durations.csv", "a") as file:
        file.write(f"{query_type},{limit},{start},{end},{duration}\n")
    records = cursor
    print(records)


############################### benchmark cases ###############################

def execute_query(query="SELECT * FROM cycling_data", query_type="surrounding", limit=50):
    """
    Executes different spatial or spatiotemporal benchmark queries on a PostgreSQL database.

    Parameters:
    - query (str): Base SQL query to execute (default is "SELECT * FROM cycling_data").
    - query_type (str): Type of query to execute. It determines the benchmark being run.
    - limit (int): Maximum number of rows to return (used in specific cases).

Benchmarks:
    - Spatial Queries:
      - "surrounding": Finds all points within a 5000m radius of a random point in Berlin.
      - "bounding_box": Finds all points within a dynamically generated bounding box near Berlin.
      - "polygonal_area": Finds all points inside a static polygon defined by random vertices in Berlin.
      - "nearest_neighbor": Finds the closest point to a random position in Berlin.
      - "clustering": Groups data points into spatial clusters using K-Means.

    - Trip/Trajectory Queries:
      - "ride_traffic": Checks intersections between trips to identify overlapping rides.
      - "trajectory_analysis": Identifies intersections between trajectories and analyzes paths.
      - "trajectory_length": Calculates the total length of each trajectory.
      - "trajectory_duration": Computes the duration of each trajectory.
      - "trajectory_speed": Determines the average speed of each trajectory.
      - "trajectory_density": Analyzes the density of points along each trajectory.

    - Spatiotemporal Queries:
      - "time_interval": Filters data by a specific time range.
      - "spatiotemporal": Combines spatial (points within a radius) and temporal (timestamps) filters.
      - "interval_around_timestamp": Finds data points within 1 hour of a specific timestamp.
      - "trajectory_within_time_interval": Filters trajectories that exist entirely within a given time range.
      - "count_points_in_time_range": Counts the number of points collected during a specific time interval.
      - "temporal_changes_in_region": Filters points in a specific area to track their changes over time.
      - "average_speed_in_time_range": Calculates the average speed of trips occurring within a specific time frame.
      - "event_duration_in_region": Measures the duration of events (e.g., trips) occurring in a defined region.
      - "peak_activity_times": Identifies the most active time ranges in the dataset.

    Returns:
    Writes execution duration and results to "durations.csv" for benchmarking purposes.
    """

    try:
        connection = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="test",
            host=hostname,
            port=portnum
        )
        query_table = "cycling_trips_ref" if deployment == "multi" else "cycling_trips"

        match query_type:
            ########################### SPATIAL QUERIES ###########################
            case "surrounding":
                poslong, poslat = generate_random_position_in_Berlin()
                query_addition = f"""
                    WHERE ST_DWithin(
                        cycling_data.point_geom::geography,
                        ST_SetSRID(ST_MakePoint({poslong}, {poslat}), 4326)::geography,
                        5000
                    );
                """
                execute_and_log_query(connection, query, query_addition, query_type, limit)

            case "bounding_box":
                poslong, poslat = generate_random_position_in_Berlin()
                query_addition = f"""
                    WHERE ST_Intersects(
                        cycling_data.point_geom::geography,
                        ST_MakeEnvelope({poslong - 0.1}, {poslat - 0.1}, {poslong + 0.1}, {poslat + 0.1}, 4326)::geography
                    ) LIMIT {limit};
                """
                execute_and_log_query(connection, query, query_addition, query_type, limit)

            case "polygonal_area":
                lat1, lon1 = generate_random_position_in_Berlin()
                lat2, lon2 = generate_random_position_in_Berlin()
                lat3, lon3 = generate_random_position_in_Berlin()
                query_addition = f"""
                    WHERE ST_Intersects(
                        cycling_data.point_geom::geography,
                        ST_GeomFromText(
                            'POLYGON(({lon1} {lat1}, {lon2} {lat2}, {lon3} {lat3}, {lon1} {lat1}))',
                            4326
                        )::geography
                    ) LIMIT {limit};
                """
                execute_and_log_query(connection, query, query_addition, query_type, limit)

            case "nearest_neighbor":
                poslong, poslat = generate_random_position_in_Berlin()
                query_addition = f"""
                    ORDER BY
                        point_geom <-> ST_SetSRID(ST_MakePoint({poslong}, {poslat}), 4326)
                    LIMIT {limit};
                """
                execute_and_log_query(connection, query, query_addition, query_type, limit)

            case "clustering":
                num_clusters = 5  # Define the number of clusters
                query_addition = f"""
                    SELECT
                        ST_ClusterKMeans(point_geom, {num_clusters}) OVER () AS cluster_id,
                        *
                    FROM
                        cycling_data
                    LIMIT {limit};
                """
                execute_and_log_query(connection, query_addition, "", query_type, limit)

            ########################### TRIP/TRAJECTORY QUERIES ###########################
            case "ride_traffic":
                ride_id = random.randint(1, 596)
                query_addition = f"""
                    SELECT a.ride_id AS trip_id_1, b.ride_id AS trip_id_2, a.trip && b.trip AS intersects
                    FROM {query_table} a
                    JOIN {query_table} b ON a.ride_id <> b.ride_id
                    WHERE a.ride_id = {ride_id} AND a.trip && b.trip
                    LIMIT {limit};
                """
                execute_and_log_query(connection, "", query_addition, query_type, limit)

            case "trajectory_analysis":
                ride_id = random.randint(1, 596)
                query_addition = f"""
                    SELECT
                        a.ride_id AS trip_id_1,
                        b.ride_id AS trip_id_2,
                        ST_Intersection(a.trip, b.trip) AS intersection_geom
                    FROM
                        {query_table} a
                    JOIN
                        {query_table} b ON a.ride_id <> b.ride_id
                    WHERE
                        a.ride_id = {ride_id}
                        AND ST_Intersects(a.trip, b.trip)
                    LIMIT {limit};
                """
                execute_and_log_query(connection, "", query_addition, query_type, limit)

            case "trajectory_length":
                # Calculates the total length of each trajectory
                query_addition = f"""
                    SELECT
                        ride_id,
                        ST_Length(trip::geography) AS length_meters
                    FROM
                        {query_table}
                    LIMIT {limit};
                """
                execute_and_log_query(connection, "", query_addition, query_type, limit)

            case "trajectory_duration":
                # Computes the duration of each trajectory
                query_addition = f"""
                    SELECT
                        ride_id,
                        EXTRACT(EPOCH FROM (MAX(timestamp) - MIN(timestamp))) AS duration_seconds
                    FROM
                        cycling_data
                    GROUP BY
                        ride_id
                    LIMIT {limit};
                """
                execute_and_log_query(connection, "", query_addition, query_type, limit)

            case "trajectory_speed":
                # Determines the average speed of each trajectory
                query_addition = f"""
                    SELECT
                        ride_id,
                        ST_Length(trip::geography) / NULLIF(EXTRACT(EPOCH FROM (MAX(timestamp) - MIN(timestamp))), 0) AS avg_speed_mps
                    FROM
                        {query_table}
                    GROUP BY
                        ride_id
                    LIMIT {limit};
                """
                execute_and_log_query(connection, "", query_addition, query_type, limit)

            case "trajectory_density":
                # Analyzes the density of points along each trajectory
                query_addition = f"""
                    SELECT
                        ride_id,
                        COUNT(*) / NULLIF(ST_Length(ST_MakeLine(point_geom ORDER BY timestamp)::geography), 0) AS points_per_meter
                    FROM
                        cycling_data
                    GROUP BY
                        ride_id
                    LIMIT {limit};
                """
                execute_and_log_query(connection, "", query_addition, query_type, limit)

            ########################### SPATIOTEMPORAL QUERIES ###########################
            case "time_interval":
                start_time, end_time = generate_random_time_interval(period_start, period_end, duration)
                query_addition = f"""
                    WHERE timestamp BETWEEN '{start_time}' AND '{end_time}' LIMIT {limit};
                """
                execute_and_log_query(connection, query, query_addition, query_type, limit)

            case "spatiotemporal":
                start_time, end_time = generate_random_time_interval(period_start, period_end, duration)
                poslong, poslat = generate_random_position_in_Berlin()
                query_addition = f"""
                    WHERE timestamp BETWEEN '{start_time}' AND '{end_time}' AND
                    ST_DWithin(
                        cycling_data.point_geom::geography,
                        ST_SetSRID(ST_MakePoint({poslong}, {poslat}), 4326)::geography,
                        5000
                    ) LIMIT {limit};
                """
                execute_and_log_query(connection, query, query_addition, query_type, limit)

            case "interval_around_timestamp":
                start_time, end_time = generate_random_time_interval(period_start, period_end, duration)
                query_addition = f"""
                    WHERE timestamp BETWEEN
                        '{start_time}' - INTERVAL '1 hour' AND
                        '{start_time}' + INTERVAL '1 hour'
                    LIMIT {limit};
                """
                execute_and_log_query(connection, query, query_addition, query_type, limit)

            case "trajectory_within_time_interval":
                # Filters trajectories that exist entirely within a given time range
                start_time, end_time = generate_random_time_interval(period_start, period_end, duration)
                query_addition = f"""
                    WHERE trip && tstzrange('{start_time}', '{end_time}')
                    LIMIT {limit};
                """
                execute_and_log_query(connection, query, query_addition, query_type, limit)

            case "count_points_in_time_range":
                # Counts the number of points collected during a specific time interval
                start_time, end_time = generate_random_time_interval(period_start, period_end, duration)
                query_addition = f"""
                    SELECT COUNT(*)
                    FROM cycling_data
                    WHERE timestamp BETWEEN '{start_time}' AND '{end_time}';
                """
                execute_and_log_query(connection, "", query_addition, query_type, limit)

            case "temporal_changes_in_region":
                #  Filters points in a specific area to track their changes over time
                start_time, end_time = generate_random_time_interval(period_start, period_end, duration)
                poslong, poslat = generate_random_position_in_Berlin()
                query_addition = f"""
                    WHERE timestamp BETWEEN '{start_time}' AND '{end_time}'
                    AND ST_Within(
                        cycling_data.point_geom,
                        ST_Buffer(ST_SetSRID(ST_MakePoint({poslong}, {poslat}), 4326), 0.05)
                    )
                    LIMIT {limit};
                """
                execute_and_log_query(connection, query, query_addition, query_type, limit)

            case "average_speed_in_time_range":
                # Calculates the average speed of trips occurring within a specific time frame
                start_time, end_time = generate_random_time_interval(period_start, period_end, duration)
                query_addition = f"""
                    SELECT AVG(speed)
                    FROM cycling_data
                    WHERE timestamp BETWEEN '{start_time}' AND '{end_time}';
                """
                execute_and_log_query(connection, "", query_addition, query_type, limit)

            case "event_duration_in_region":
                # Measures the duration of events (e.g., trips) occurring in a defined region
                start_time, end_time = generate_random_time_interval(period_start, period_end, duration)
                poslong, poslat = generate_random_position_in_Berlin()
                query_addition = f"""
                    SELECT ride_id, MAX(timestamp) - MIN(timestamp) AS duration
                    FROM cycling_data
                    WHERE timestamp BETWEEN '{start_time}' AND '{end_time}'
                    AND ST_DWithin(
                        point_geom::geography,
                        ST_SetSRID(ST_MakePoint({poslong}, {poslat}), 4326)::geography,
                        1000
                    )
                    GROUP BY ride_id;
                """
                execute_and_log_query(connection, query, query_addition, query_type, limit)

            case "peak_activity_times":
                # Most active time ranges in the dataset
                query_addition = f"""
                    SELECT date_trunc('hour', timestamp) AS hour, COUNT(*)
                    FROM cycling_data
                    GROUP BY hour
                    ORDER BY COUNT(*) DESC
                    LIMIT {limit};
                """
                execute_and_log_query(connection, "", query_addition, query_type, limit)


    except (Exception, psycopg2.Error) as error:
        print(f"Error executing query '{query_type}':", error)
    finally:
        if connection:
            connection.close()



############################### benchmark execution ###############################
# List of queries to execute
def run_threads(num_threads, query, query_type, limit):
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=execute_query, args=(query, query_type, limit))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
        # clear the threads list
        threads.clear()

# Create and start a thread until the number of threads is reached
# run mini benchmark

#initial insert of data if not done on machine, 
#clear_table('cycling_data')
#clear_table('cycling_trips')
#initial_insert()


#Configure the benchmark
#run_threads(#Number of parallel threads, default query to use, query type, limit)
run_threads(2, default_query, "surrounding", 50)
run_threads(2, default_query, "ride_traffic", 50)
run_threads(2, default_query, "intersections", 50)
run_threads(2, default_query, "insert_ride", 10)
run_threads(1, default_query, "bulk_insert_rides", 10)
run_threads(2, default_query, "bounding_box", 50)
run_threads(2, default_query, "polygonal_area", 50)
run_threads(2, default_query, "time_interval", 50)
run_threads(2, default_query, "get_trip", 50)
run_threads(2, default_query, "get_trip_length", 50)
run_threads(2, default_query, "get_trip_duration", 50)
run_threads(2, default_query, "get_trip_speed", 50)
#run_threads(2, default_query, "interval_around_timestamp", 50)
#run_threads(2, default_query, "spatiotemporal", 50)
