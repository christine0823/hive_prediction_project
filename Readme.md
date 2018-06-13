## Readme

### Data collection
* Running on Hadoop 2.7.1 + Hive 2.3.0
* Workload : [https://github.com/hortonworks/hive-testbench](https://)
#### Run query logs and collect logs
* sudo apt-get install jq ==(for json format)==

#### Profile and generate training data
* genTrainingData 
    * Per query
        * Total running time
        * DAG_sequence_length
        * Dataset scale
        * Hadoop and Hive configurations
    * Per job
        * Job execution time
        * Operation type
        * Input_reocrds 
    * Generate output
    ```javascript
    bash genPredictionTrainingData.sh [query].log ../data/[query].csv
    ```
* data
    * query2.csv/query3.csv/query5.csv/query8.csv

### Oracle
* 2-step prediction
    * DAG prediction model
        * sequence_length
        ```javascript
        python main.py --i [inputdata].csv 
                       --m [save_root_dir]
        
        * Output
            * scaler file : [save_root_dir]_jobInfo.scl.pkl
            * model file : [save_root_dir]_seqLen.h5
        ```
        * jobinfo_model
    * Time prediction model
        ```javascript
        python main.py --i [inputdata].csv 
                       --m [save_root_dir]
                       
        E.g. python main.py --i ../../data_collection/data/query2.csv 
                       --m ../models/query2
        
        * Output
            * scaler file : [save_root_dir]_time.scl.pkl
            * model file : [save_root_dir]_time.h5
        ```
    * Test
    
* testing
    * Predefined scaler/binarylabel/model file
        
### Optimization

### Baseline
* Equation
* Simulation
* DNN
