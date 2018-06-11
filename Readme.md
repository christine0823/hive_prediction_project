## Oracle: A Deep Learning Model for Predicting andOptimizing Complex Query Workflow

### Data collection
* Running on Hadoop 2.7.1 + Hive 2.3.0
* Workload : [https://github.com/hortonworks/hive-testbench](https://)
* sudo apt-get install jq ==(for json format)==
* hadoop-logs : query2 / query3 /query5 / query8
* genTrainingData 
    * ==Per query==
        * total_running_time, DAG_sequence_length
    * ==Per job== : 
        * job_execution_time, operation_type, input_reocrds, dataset(++estimated total records++) ,[Hadoop and Hive configurations]
    * Generate output
    ```javascript
    bash genPredictionTrainingData.sh [query].log ../data/[query].csv
    ```

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
