# Requirements for running the benchmark
You'll need to pass the the GCP_IP of your main instance in order to run queries. Additionally, you'll need Python with the following installed packages at least:
```
pyyaml
```

You can then run the benchmark using the following command, with deployment type being either "single" or "multi", depending on your currently deployed system
```
python runMiniBenchmark.py <GCP_IP> <deployment_type>
```
Example:
```
python runMiniBenchmark.py 32.219.34.10 single
```

## What does the benchmark contain
As of now, the benchmark contains the query types for cycling data:
- "surrounding"
Gets data points surrounding a generated data point
- "ride_traffic"
gets intersections of rides
- "intersections"
Gets intersections of a specific ride_id
- "bounding_box"
Gets data contained by a bounding box
- "polygonal_area"
Gets data defined by a polygonal area
- "time_interval"
Gets data in a certain time interval
- "get_trip"
Gets a specific trip

## Usage
The `run_threads` function takes three parameters:
- Number of threads
Define the parallelism of requests made to the database
- Default query
Used in some queries to add a "SELECT * FROM cycling_data" beforehand
- Limit
This limits the number of results provided to you in certain queries.
