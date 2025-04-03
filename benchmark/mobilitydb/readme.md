# Requirements for running the benchmark
You'll need to pass the the GCP_IP of your main instance in order to run queries. Additionally, you'll need Python with the following installed packages at least:
```
psycopg2
```

You can then run the benchmark using the following command, with "5432" being the default port of PostgreSQL servers (which MobilityDB is based on )
```
python runMiniBenchmark.py <GCP_IP> 5432 single/multi
```
Example:
```
python runMiniBenchmark.py 32.219.34.10 5432 single
```

## What does the benchmark contain
As of now, the benchmark contains the query types for cycling data:
- "surrounding"
Gets data points surrounding a generated data point
- "ride_traffic"
gets intersections of rides
- "intersections"
Gets intersections of a specific ride_id
- "insert_ride"
Inserts rides into the table
- "bulk_insert_rides"
Inserts more rides into the table
- "bounding_box"
Gets data contained by a bounding box
- "polygonal_area"
Gets data defined by a polygonal area
- "time_interval"
Gets data in a certain time interval
- "get_trip"
Gets a specific trip
- "get_trip_length"
Gets the length of a trip
- "get_trip_duration"
Gets the duration of the trip
- "get_trip_speed"
Gets the trip speed at each data point

## Usage
The `run_threads` function takes three parameters:
- Number of threads
Define the parallelism of requests made to the database
- Default query
Used in some queries to add a "SELECT * FROM cycling_data" beforehand
- Limit
This limits the number of results provided to you in certain queries.
