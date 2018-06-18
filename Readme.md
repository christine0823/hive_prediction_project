# Oracle: A Deep Learning Model for Predicting and Optimizing Complex Query Workflow

## Data collection
#### Run query logs and collect logs
* Running on Hadoop 2.7.1 + Hive 2.3.0
* Workload : [https://github.com/hortonworks/hive-testbench](https://)
* sudo apt-get install jq ==(for json format)==
* Setup
    ```javascript
    bash setup_metastore.sh
    cp -r metastore_db prediction_data_generate/
    ```
* Run hive queies
    ```javascript
    bash run_hive.sh [query index] [datasets]
    E.g. bash run_hive.sh 1 4
    ```
    * Input : hive-testbench/sample-queries-tpch/tpch_query${sqlid}.sql
    * Output : hive-testbench/prediction_data_generate/logs/query${sqlid}.log
    
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
        * json logs to csv
    ```javascript
    bash genPredictionTrainingData.sh query${sqlid}.log ../data/query${sqlid}.csv
    ```
* data
    * query2.csv/query3.csv/query5.csv/query8.csv


## Oracle
### 2-step prediction

#### DAG prediction model
* sequence_length
    * Input : DAG configurations
    * Output
        - scaler file : [save_root_dir]_jobInfo.scl.pkl
        - model file : [save_root_dir]_seqLen.h5
* jobinfo_model
    * Input : DAG configurations
    * Output
        - model file : [save_root_dir]_jobInfo.h5
#### Time prediction model 
* Input : all configurations and information
* Output
    - scaler file : [save_root_dir]_time.scl.pkl
    - model file : [save_root_dir]_time.h5

#### Command for Training models
```javascript
    python main.py --i [inputdata].csv 
                   --m [save_root_dir]

    E.g. python main.py --i ../../data_collection/data/query2.csv\ 
                        --m ../models/query2
```                   

* Evaluation
    * Predefined scaler/label/model file
    * Input : all configurations and information
    * Output:
        - predicted SeqLen and jobInfo
        - predicted total running time
        
#### Command for evaluation
```javascript
    python main.py --i [inputdata].csv --q query${sqlid}

    E.g. python main.py --i ../../data_collection/data/query2.csv\ 
                        --q query2
```                   
        
### Optimization
* Hive optimization
    * Input : 
        * bound_only_dag.csv (all DAG-dependent configurtaions)
    * Output : output.csv / output_dag
    ```javascript
    python main_hive.py --i bound_only_dag.csv --o output 
                        --s [scale] --q query${sqlid}
    
    E.g. python main_hive.py --i bound_only_dag.csv --o output\
                             --s 5 --q query2
    ```
* Hadoop optimization
    * Input : output.csv
    * Output : output_all
    ```javascript
    python main_hadoop.py --i bound_only_dag.csv --o output
                        --s [scale] --q query${sqlid}
    
    E.g. python main_hadoop.py --i output.csv --o output --s 5 --q query2
    ```

### Baseline
* Equation
    * Input
        * dags/dag${idx}.csv
        * testtypes/${operation}.csv
        * workflow equation for DAG structure
    * Output 
        * Each job time
        * Total running time
```javascript
    python equation.py
```
* Simulation
    * Install mrperf
        * http://research.cs.vt.edu/dssl/mrperf/
    * Run simulation
        * Input 
            mrperf/test/simulation/simulation${DAGidx}.csv
        * Output
            mrperf/test/time/${DAGidx} _ ${Jobidx}.out
    ```javascript
    cd mrperf/test
    bash run.sh [DAGidx] [Datasetidx] [JobLen]
    ```
* DNN
    * Input : Hive and Hadoop configurations
```javascript
    python main.py --i ~/hive_prediction_project/data/query${sqlid}.csv
```
