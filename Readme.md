## Data-driven Solution on Hive for Execution Time Prediction and Optimization

### Data collection
* Running on Hadoop 2.7.1 + Hive 2.3.0
* Workload : hive-testbench
[https://github.com/hortonworks/hive-testbench](https://)
* sudo apt-get install jq ==(for json format)==
* hadoop-logs : query2 / query3 /query5 / query8
* genTrainingData 

### 2-step prediction
* 2-step prediction
    * plan prediction model
        * sequence_length
        * jobinfo_model
    * time prediction model
        * rnn_multidag_model
        ```javascript
        python main.py --i [inputdata].csv 
                       --s [predefined scalerfile].scl.pkl 
                       --m [save_model_path]
        ```
    * testing
### Optimization

### Baseline
* Equation
* Simulation
* DNN
