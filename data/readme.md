# SimRa
In order to test your system with cycling data, you can download data into the `SimRa` folder either from Github or DepositOnce (Links found in the GitHub repository). However, there is also one month of data within this repository itself you can use to get started:
```
https://github.com/simra-project/dataset
```
Once you've downloaded the data into the folder (the script checks subfolders, no need to move the VM2 files), you can run the `prepareCyclingData.py`script to turn those files into MobilityDB and Geomesa-appropiate files, which will be stored in the `data` folder. Make sure to run the script from the `data` folder.  
You should then have four types of files:
```
merged*.csv (MobilityDB point data)
trips_merged*.csv (MobilityDB trip data)
geomesa_merged*.csv (GeoMesa point data)
geomesa_trips_geomesa_merged*.csv (GeoMesa trip data)
```