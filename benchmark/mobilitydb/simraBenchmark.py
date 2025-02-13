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

if len(sys.argv) != 4:
    print("Usage: python3 script_name.py <hostname> <portnum> <deployment>")
    sys.exit(1)

# Configuration
hostname = sys.argv[1]
portnum = sys.argv[2]
deployment = "multi" if len(sys.argv) < 4 else sys.argv[3]
default_query = "SELECT * FROM cycling_data"

#Timeframe for spatiotemporal queries
period_start = "2023-07-01 00:00:00"
period_end = "2023-07-31 23:59:59"
duration = timedelta(hours=2)

# Utility functions: Generate random position in Berlin
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

def execute_and_log_query(connection, base_query, query_addition, query_type, limit):
    """Helper function to execute a query and log its duration."""
    cursor = connection.cursor()
    full_query = base_query + query_addition
    print(full_query)
    start = time.time()
    cursor.execute(full_query)
    end = time.time()
    duration = end - start
    with open("mobilitydb-simra-durations.csv", "a") as file:
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

Benchmark:
    - Spatial Queries:
      - "surrounding": Finds all points within a 5000m radius of a random point in Berlin.
      - "bounding_box": Finds all points within a dynamically generated bounding box near Berlin.
      - "polygonal_area": Finds all points inside a static polygon defined by random vertices in Berlin.
      - "nearest_neighbor": Finds the closest point to a random position in Berlin.
      - "clustering": Groups data points into spatial clusters using K-Means.
      - "line_proximity": Finds points within 500m of a randomly generated line in Berlin.

    - Trip Queries:
      - "ride_traffic": Checks intersections between trips to identify overlapping rides.
      - "trajectory_intersections": Identifies intersections and intersection geometries between trajectories.
      - "trip_length": Calculates the total length of each trip/trajectory.
      - "trip_duration": Computes the duration of each trip/trajectory.
      - "trajectory_speed": Calculates the average speed of each trajectory based on distance and time.
      - "trajectory_density": Analyzes the density of points along each trajectory.

    - Attribute-Based Queries:
      - "attribute_value_filter_points": Filters point data where `rider_id` falls within a random interval.
      - "attribute_value_filter_trips": Filters trips where `rider_id` falls within a random interval.

    - Spatiotemporal Queries:
      - "time_interval": Retrieves all data within a specific time range.
      - "spatiotemporal_surrounding": Combines spatial proximity and a time range filter.
      - "interval_around_timestamp": Retrieves all points within 1 hour before and after a random timestamp.
      - "count_points_in_time_range": Counts the number of points collected during a specific time interval.
      - "average_speed_in_time_range": Calculates the average speed of trips within a specific time range.
      - "event_duration_in_region": Measures the duration of events occurring in a defined spatial region.
      - "peak_activity_times": Identifies the most active time ranges in the dataset.
      - "recurring_time_queries": Checks if a rider visits the same location daily for a week.

    - Advanced Queries:
      - "historical_spatiotemporal": Retrieves past data for a specific location and time range.
      - "points_after_timestamp": Retrieves points with a timestamp greater than a random timestamp.
      - "trips_starting_after_timestamp": Retrieves trips starting after a random timestamp.

    Returns:
    Writes execution duration and results to "mobilitydb-simra-durations.csv" for benchmarking purposes.
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
                        ST_ClusterKMeans(point_geom::geometry, {num_clusters}) OVER () AS cluster_id,
                        *
                    FROM
                        cycling_data
                    LIMIT {limit};
                """
                execute_and_log_query(connection, query_addition, "", query_type, limit)

            case "line_proximity":
                # Define a random line using two points in Berlin
                poslong1, poslat1 = generate_random_position_in_Berlin()
                poslong2, poslat2 = generate_random_position_in_Berlin()
                distance_threshold = 500  # Define proximity distance in meters

                query_addition = f"""
                        WHERE ST_DWithin(
                            cycling_data.point_geom::geography,
                            ST_MakeLine(
                                ST_SetSRID(ST_MakePoint({poslong1}, {poslat1}), 4326),
                                ST_SetSRID(ST_MakePoint({poslong2}, {poslat2}), 4326)
                            )::geography,
                            {distance_threshold}
                        );
                    """
                execute_and_log_query(connection, query, query_addition, query_type, limit)

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

            case "trajectory_intersections ":
                ride_id = random.randint(1, 596)
                query_addition = f"""
                    SELECT
                        a.ride_id AS trip_id_1,
                        b.ride_id AS trip_id_2,
                        ST_Intersection(trajectory(a.trip), trajectory(b.trip)) AS intersection_geom
                    FROM
                        {query_table} a
                    JOIN
                        {query_table} b ON a.ride_id <> b.ride_id
                    WHERE
                        a.ride_id = {ride_id}
                        AND ST_Intersects(trajectory(a.trip), trajectory(b.trip))
                    LIMIT {limit};
                """
                execute_and_log_query(connection, "", query_addition, query_type, limit)

            case "trip_length":
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

            case "trip_duration":
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
                        length(trip) / NULLIF(EXTRACT(EPOCH FROM duration(trip)), 0) AS avg_speed_mps
                    FROM
                        {query_table}
                    LIMIT {limit};
                """
                execute_and_log_query(connection, "", query_addition, query_type, limit)

            case "trajectory_density":
                # Analyzes the density of points along each trajectory
                query_addition = f"""
                    SELECT
                        ride_id,
                        COUNT(*) / NULLIF(ST_Length(ST_MakeLine(point_geom::geometry ORDER BY timestamp)::geography), 0) AS points_per_meter
                    FROM
                        cycling_data
                    GROUP BY
                        ride_id
                    LIMIT {limit};
                """
                execute_and_log_query(connection, "", query_addition, query_type, limit)

            case "attribute_value_filter_points":
                # Filter points with a rider_id within a random interval
                lower_rider_id = random.uniform(1, 1000)
                upper_rider_id = lower_rider_id + random.uniform(1, 42)

                query_addition = f"""
                    SELECT 
                        ride_id,
                        rider_id,
                        latitude,
                        longitude,
                        timestamp
                    FROM 
                        cycling_data
                    WHERE 
                        rider_id BETWEEN {lower_rider_id} AND {upper_rider_id}
                    LIMIT {limit};
                """
                execute_and_log_query(connection, "", query_addition, query_type, limit)

            case "attribute_value_filter_trips":
                # Filter trips with a rider_id within a random interval
                lower_rider_id = random.uniform(1, 1000)  # Generate random lower bound
                upper_rider_id = lower_rider_id + random.uniform(1, 42)  # Generate random upper bound

                query_addition = f"""
                        SELECT 
                            ride_id,
                            rider_id,
                            trip
                        FROM 
                            cycling_trips
                        WHERE 
                            rider_id BETWEEN {lower_rider_id} AND {upper_rider_id}
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

            case "spatiotemporal_surrounding":
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
                        TIMESTAMP '{start_time}' - INTERVAL '1 hour' AND
                        TIMESTAMP '{start_time}' + INTERVAL '1 hour'
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

            case "average_speed_in_time_range":
                # Calculates the average speed of trips occurring within a specific time frame
                start_time, end_time = generate_random_time_interval(period_start, period_end, duration)
                query_addition = f"""
                        SELECT AVG(distance / NULLIF(time_diff, 0)) AS avg_speed_mps
                        FROM (
                            SELECT
                                ride_id,
                                ST_Length(ST_MakeLine(point_geom::geometry ORDER BY timestamp)::geography) AS distance,  -- Distance in meters
                                EXTRACT(EPOCH FROM (MAX(timestamp) - MIN(timestamp))) AS time_diff  -- Time in seconds
                            FROM
                                cycling_data
                            WHERE
                                timestamp BETWEEN '{start_time}' AND '{end_time}'
                            GROUP BY
                                ride_id
                        ) subquery;
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
                execute_and_log_query(connection, "", query_addition, query_type, limit)

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

            case "recurring_time_queries":
                # Check if a rider_id has points within 50m of the start point daily for a week
                rider_id = random.randint(1, 1000)
                start_time, _ = generate_random_time_interval(period_start, period_end, duration=timedelta(days=7))
                query_addition = f"""
                    WITH start_point AS (
                        SELECT point_geom, timestamp
                        FROM cycling_data
                        WHERE rider_id = {rider_id}
                        ORDER BY timestamp
                        LIMIT 1
                    ),
                    proximity_checks AS (
                        SELECT
                            COUNT(DISTINCT date_trunc('day', cd.timestamp)) AS days_in_proximity
                        FROM
                            cycling_data cd,
                            start_point sp
                        WHERE
                            cd.rider_id = {rider_id}
                            AND ST_DWithin(cd.point_geom::geography, sp.point_geom::geography, 50)  
                            AND cd.timestamp BETWEEN '{start_time}' AND '{start_time}' + INTERVAL '7 days'
                    )
                    SELECT
                        {rider_id} AS rider_id,
                        '{start_time}' AS start_time,
                        '{start_time}' + INTERVAL '7 days' AS end_time,
                        CASE
                            WHEN days_in_proximity = 7 THEN 'Recurring Proximity Found'
                            ELSE 'Recurring Proximity Not Found'
                        END AS result
                    FROM proximity_checks;
                """
                execute_and_log_query(connection, "", query_addition, query_type, limit)


            case "historical_spatiotemporal":
                # Retrieve past data for a specific location and time range
                start_time, end_time = generate_random_time_interval(period_start, period_end, duration)
                poslong, poslat = generate_random_position_in_Berlin()
                query_addition = f"""
                    WHERE timestamp BETWEEN '{start_time}' AND '{end_time}'
                    AND ST_DWithin(
                        cycling_data.point_geom::geography,
                        ST_SetSRID(ST_MakePoint({poslong}, {poslat}), 4326)::geography,
                        5000
                    )
                    LIMIT {limit};
                """
                execute_and_log_query(connection, query, query_addition, query_type, limit)

################################ Temporal queries ################################

            case "points_after_timestamp":
                # Retrieves all points with a timestamp greater than a random timestamp
                random_timestamp = generate_random_time_interval(period_start, period_end, duration)
                query_addition = f"""
                        WHERE timestamp > '{random_timestamp}'
                        LIMIT {limit};
                    """
                execute_and_log_query(connection, query, query_addition, query_type, limit)


            case "trips_starting_after_timestamp":
                # Retrieves all trips that start after a random timestamp
                random_timestamp = generate_random_time_interval(period_start, period_end, duration)
                query_addition = f"""
                        WHERE trip && tstzrange('{random_timestamp}', NULL)
                        LIMIT {limit};
                    """
                execute_and_log_query(connection, query, query_addition, query_type, limit)





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

###################################### Configure the benchmark ######################################
# --------------------- SPATIAL QUERIES ---------------------
#run_threads(2, default_query, "surrounding", 500)
#run_threads(2, default_query, "bounding_box", 50)
#run_threads(2, default_query, "polygonal_area", 50)
#run_threads(2, default_query, "nearest_neighbor", 50)
#run_threads(2, default_query, "clustering", 50)
#run_threads(2, default_query, "line_proximity", 50)
#run_threads(2, default_query, "geometry_intersection", 50)

# --------------------- TRIP/TRAJECTORY QUERIES ---------------------
#run_threads(2, default_query, "ride_traffic", 50)
#run_threads(2, default_query, "trajectory_analysis", 50)
#run_threads(2, default_query, "trajectory_length", 50)
#run_threads(2, default_query, "trajectory_duration", 50)
#run_threads(2, default_query, "trajectory_speed", 50)
#run_threads(2, default_query, "trajectory_density", 50)
#run_threads(2, default_query, "attribute_value_filter", 50)
run_threads(2, default_query, "min_max_summaries", 50)


# --------------------- SPATIOTEMPORAL QUERIES ---------------------
#run_threads(2, default_query, "time_interval", 50)
#run_threads(2, default_query, "spatiotemporal", 50)
#run_threads(2, default_query, "interval_around_timestamp", 50)
#run_threads(2, default_query, "count_points_in_time_range", 50)
#run_threads(2, default_query, "temporal_changes_in_region", 50)
#run_threads(2, default_query, "average_speed_in_time_range", 50)
#run_threads(2, default_query, "event_duration_in_region", 50)
#run_threads(2, default_query, "peak_activity_times", 50)
#run_threads(2, default_query, "recurring_time_queries", 50)
#run_threads(2, default_query, "historical_spatiotemporal", 50)
