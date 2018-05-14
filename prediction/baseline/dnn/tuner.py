#!/usr/bin/env python
#
# Optimize blocksize of apps/mmm_block.cpp
#
# This is an extremely simplified version meant only for tutorials
#
import opentuner
from opentuner import ConfigurationManipulator
from opentuner import IntegerParameter
from opentuner import FloatParameter
from opentuner import MeasurementInterface
from opentuner import Result
import sys

class GccFlagsTuner(MeasurementInterface):

  def manipulator(self):
    """
    Define the search space by creating a
    ConfigurationManipulator
    """
    manipulator = ConfigurationManipulator()
    manipulator.add_parameter(IntegerParameter('batch_size', 5, 200))
    manipulator.add_parameter(IntegerParameter('layer', 1, 20))
    manipulator.add_parameter(IntegerParameter('neural', 50, 200))
    #manipulator.add_parameter(IntegerParameter('max_iter', 1, 500))
    #manipulator.add_parameter(FloatParameter('learning_rate_init', 0.0001, 0.01))
    #manipulator.add_parameter(FloatParameter('power_t', 0.2, 0.8))
    #manipulator.add_parameter(FloatParameter('alpha', 0.00001, 0.001))

    return manipulator

  def run(self, desired_result, input, limit):
    """
    Compile and run a given configuration then
    return performance
    """
    cfg = desired_result.configuration.data
    
    run_cmd = 'python main.py --i ../optimizer/log.terasort.all.csv --l ../optimizer/log.terasort.all.labeled.csv --o result.terasort --SOLVER lbfgs '+ \
	' --BATCH_SIZE ' + str(cfg['batch_size']) + \
	' --NUM_LAYER ' + str(cfg['layer']) + \
	' --NUM_NEURAL ' + str(cfg['neural']) 
#	' --MAX_ITER ' + str(cfg['max_iter']) + \
#	' --L_R_INIT ' + str(cfg['learning_rate_init']) + \
#	' --POWER_T ' + str(cfg['power_t']) + \
#	' --ALPHA ' + str(cfg['alpha'])
    print run_cmd,
    sys.stdout.flush()
    run_result = self.call_program(run_cmd)
    assert run_result['returncode'] == 0

    f = open('tuning_mean', 'r')
    error = float(f.read())
    error = error
    print error
    sys.stdout.flush()

    return Result(time=error)

  def save_final_config(self, configuration):
    """called at the end of tuning"""
    print "Optimal block size written to mmm_final_config.json:", configuration.data
    self.manipulator().save_to_file(configuration.data,
                                    'mmm_final_config.json')


if __name__ == '__main__':
  argparser = opentuner.default_argparser()
  GccFlagsTuner.main(argparser.parse_args())
