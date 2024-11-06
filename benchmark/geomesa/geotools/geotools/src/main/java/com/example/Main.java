package com.example;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import org.geotools.api.data.DataStore;
import org.geotools.api.data.DataStoreFinder;
import org.geotools.api.data.SimpleFeatureSource;
import org.geotools.api.feature.simple.SimpleFeature;
import org.geotools.api.feature.simple.SimpleFeatureType;
import org.geotools.api.feature.type.AttributeDescriptor;
import org.geotools.api.filter.Filter;
import org.geotools.data.simple.SimpleFeatureCollection;
import org.geotools.data.simple.SimpleFeatureIterator;
import org.geotools.filter.text.cql2.CQL;

public class Main {
    // Method to execute the queries on the datastore
    // Input: queryType:Str; limit:Int
    // Output: None
    // Functionality: Executes the query on the datastore, saves the required time in a file
    public static void executeQuery(String queryType, Integer limit){
        // Eexecute the query

        // Save the query type, start time, end time, duration, and parallelism i.e thread count in a file
    
        // Print the time
    }

    public static void runThreads(String queryType, Integer threadCount)
    {
        // Create threads

        // Start threads

        // Wait for threads to finish

    }
    //
    public static void main(String[] args) {
        System.out.println("Starting...");
        String instanceName = args[0];
        String username = args[1];
        String password = args[2];
        String catalog = args[3];
        String zookeepers = args[4];
        
        //Check the variables by printing them
        System.out.println("Instance Name: "+instanceName);
        System.out.println("Username: "+username);
        System.out.println("Password: "+password);
        System.out.println("Catalog: "+catalog);
        System.out.println("Zookeepers: "+zookeepers);
        Map<String, String> parameters = new HashMap<>();
        parameters.put("accumulo.instance.name", instanceName);
        parameters.put("accumulo.user", username);
        parameters.put("accumulo.password", password);
        parameters.put("accumulo.catalog", catalog);
        parameters.put("accumulo.zookeepers", zookeepers);
        try{
            System.out.println("Trying to connect to the datastore");
            DataStore dataStore = DataStoreFinder.getDataStore(parameters);
            System.out.println("Connected to the datastore "+dataStore);
            for (String str : dataStore.getTypeNames()) {
                System.out.println("Feature: "+str);
                SimpleFeatureSource source = dataStore.getFeatureSource(str);
                System.out.println("This is the source: "+source);
                Filter filter=null;
                Filter filter2=null;
                
                try {
                    filter= CQL.toFilter("rider_id <= 27");
                    filter2 = CQL.toFilter("rider_id <= 5");
                }catch(Exception e){
                    System.out.println("Failed to set filter");
                }
                System.out.println("This is the filter: "+filter);
                SimpleFeatureCollection allFeatures = source.getFeatures( filter2 );
                SimpleFeatureCollection limitedFeatures = source.getFeatures( filter );
                SimpleFeatureType schema = source.getSchema();
                for (AttributeDescriptor descriptor : schema.getAttributeDescriptors()) {
                   System.out.println(descriptor.getLocalName() + " - " + descriptor.getType().getBinding());
                }
                if(str.equals("trip_data")){
                    
                
                SimpleFeatureIterator it = limitedFeatures.features();
                try {
                    while (it.hasNext()) {
                        SimpleFeature feature = it.next();
                        System.out.println("This is the feature: "+feature.getAttribute("rider_id"));
                    }
                }catch(Exception e){
                    System.out.println("Failed to iterate over the features");
                    
                } finally {
                    it.close();
                }
                it = allFeatures.features();
                try {
                    while (it.hasNext()) {
                        SimpleFeature feature = it.next();
                        System.out.println("This is the feature: "+feature.getAttribute("rider_id"));
                    }
                }catch(Exception e){
                    System.out.println("Failed to iterate over the features");
                    
                } finally {
                    it.close();
                }
            }
                int count = allFeatures.size();
                int count2 = limitedFeatures.size();
                System.out.println("Number of selected features:" + count+ " ,"+count2);
            }
            dataStore.dispose();
        } catch (IOException e) {
            System.out.println("Error connecting to the datastore");
        }

        // Connecting to the datastore
    }
}
