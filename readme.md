# GeoBenchr
Welcome to Geobenchr, an application benchmark tool for single-node and distributed spatiotemporal databases.
Geobenchr currently supports both MobilityDB and GeoMesa Accumulo and other platforms are currently being worked on. 
## Getting started 
Specific documentation for setting up MobilityDB and GeoMesa can be found in their respective folders. 
However, general information for what Geobenchr aims to be can be found further below.
### GCloud authentication
Authenticate with the GCloud CLI by doing the following (GCloud CLI needs to be installed in order for this to work)
```
gcloud auth login
gcloud auth application-default login
```
You should now be authenticated with the Google Cloud. Make sure that you're in the correct project.
### Setting up Benchmark infrastructure
Please refer to the `readme` found in the respective folder for the system you want to setup for benchmark procedures.
### Included Datasets
As of now, Geobenchr relies on  data from SimRa, a cycling application. A script to convert data into a format that is usable for both databases can be found in the `data`folder.  Data can be gotten from the GitHub repository or the DepositOnce site behind it: https://github.com/simra-project/dataset?tab=readme-ov-file/ or as an example from DepositOnce: https://depositonce.tu-berlin.de/items/212ae8b8-7376-47c1-bae2-09103c622de2 
We also include aviation data, which is semi-publically available (pending a registration with the service). We plan on swapping to a more detailed dataset for our aviation application in the future, as flight data here is given with large gaps.

## Application Benchmark Queries 
Our benchmark aims to support various query types, as applications may have varying requests to a database depending on the kind of application. While several query types are discussed, we focus on those listed below. Additionally, we differ between queries which require near-realtime responses and ones used for an analysis aspect. All of the queries listed below can be formulated both as realtime and analysis queries, depending on the scope.
1. Spatial Queries
- Bounding Box Queries: Retrieve data within a defined rectangular area.  
- Polygonal Queries: Retrieve data within a specified polygonal area.  
- Proximity Queries: Retrieve data within a certain distance from a point or line.  
- Intersection Queries: Retrieve data that intersects with a specified geometry.  
2. Temporal Queries
- Time Slice Queries: Retrieve data for a specific time or timestamp.  
- Time Range Queries: Retrieve data within a specified time range.  
- Relative Time Queries: Retrieve data relative to the current time, such as the last hour, day, or week.  
- Recurring Time Queries: Retrieve data that matches recurring time intervals, such as daily, weekly, or monthly patterns.  
3. Spatiotemporal Queries
- Spatiotemporal Range Queries: Retrieve data within a specified spatial area and time range.  
- Trajectory Queries: Retrieve data that follows a moving object's path over time.  
- Historical Spatiotemporal Queries: Retrieve past data for specified locations and times.  
- Predictive Queries: Retrieve forecasted data based on historical patterns in both space and time.  
4. Attribute Queries
- Value-Based Queries: Retrieve data based on specific attribute values or ranges.  
- Statistical Queries: Retrieve aggregated or statistical summaries of data, such as averages, counts, or sums, within specified spatiotemporal extents.  
- Threshold Queries: Retrieve data where attribute values exceed or fall below certain thresholds.
5. Combined Queries
- Complex Queries: Combine spatiotemporal and attribute conditions to retrieve data that meets multiple criteria.  