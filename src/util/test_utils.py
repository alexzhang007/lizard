#=========================================================================
# test_utils
#=========================================================================
# Simple helper test functions.

from pymtl import *
import collections
import re


class RunTestVectorSimError( Exception ):
  pass


#-------------------------------------------------------------------------
# mk_test_case_table
#-------------------------------------------------------------------------


def mk_test_case_table( raw_test_case_table ):

  # First row in test vectors contains port names

  if isinstance( raw_test_case_table[ 0 ], str ):
    test_param_names = raw_test_case_table[ 0 ].split()
  else:
    test_param_names = raw_test_case_table[ 0 ]

  TestCase = collections.namedtuple( "TestCase", test_param_names )

  ids = []
  test_cases = []
  for row in raw_test_case_table[ 1:]:
    ids.append( row[ 0 ] )
    test_cases.append( TestCase(*row[ 1:] ) )

  return {
      'ids': ids,
      'argnames': ( 'test_params' ),
      'argvalues': test_cases,
  }


#-------------------------------------------------------------------------
# run sim
#-------------------------------------------------------------------------


def run_sim( model, dump_vcd=None, test_verilog=False, max_cycles=5000 ):

  # Setup the model

  model.vcd_file = dump_vcd
  if test_verilog:
    model = TranslationTool( model )
  model.elaborate()

  # Create a simulator

  sim = SimulationTool( model )

  # Reset model

  sim.reset()
  print()

  # Run simulation

  while not model.done() and sim.ncycles < max_cycles:
    sim.print_line_trace()
    sim.cycle()

  # Force a test failure if we timed out

  assert sim.ncycles < max_cycles

  # Extra ticks to make VCD easier to read

  sim.cycle()
  sim.cycle()
  sim.cycle()


#-------------------------------------------------------------------------
# run_test_vector_sim
#-------------------------------------------------------------------------


def run_test_vector_sim( model,
                         test_vectors,
                         dump_vcd=None,
                         test_verilog=False ):

  # First row in test vectors contains port names

  if isinstance( test_vectors[ 0 ], str ):
    port_names = test_vectors[ 0 ].split()
  else:
    port_names = test_vectors[ 0 ]

  # Remaining rows contain the actual test vectors

  test_vectors = test_vectors[ 1:]

  # Setup the model

  model.vcd_file = dump_vcd
  if test_verilog:
    model = TranslationTool( model )
  model.elaborate()

  # Create a simulator

  sim = SimulationTool( model )

  # Reset model

  sim.reset()
  print ""

  for row_num, row in enumerate( test_vectors ):
    for port_name, in_value in zip( port_names, row ):
      if port_name[-1 ] != "*":
        exec ( "model.{}.v = in_value".format( port_name ) )

    sim.eval_combinational()
    sim.print_line_trace()

    for port_name, ref_value in zip( port_names, row ):
      if port_name[-1 ] == "*":
        exec ( "out_value = model.{}".format( port_name[ 0:-1 ] ) )
        if ( ref_value != '?' ) and ( out_value != ref_value ):
          error_msg = """
 run_test_vector_sim received an incorrect value!
  - row number     : {row_number}
  - port name      : {port_name}
  - expected value : {expected_msg}
  - actual value   : {actual_msg}
"""
          raise RunTestVectorSimError(
              error_msg.format(
                  row_number=row_num,
                  port_name=port_name,
                  expected_msg=ref_value,
                  actual_msg=out_value ) )

    # Tick the simulation

    sim.cycle()

  # Extra ticks to make VCD easier to read

  sim.cycle()
  sim.cycle()
  sim.cycle()
