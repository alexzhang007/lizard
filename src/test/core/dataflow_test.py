import pytest
from pymtl import *
from model.test_model import run_test_state_machine
from core.rtl.dataflow import DataFlowManager
from core.fl.dataflow import DataFlowManagerFL
from model.wrapper import wrap_to_cl


@pytest.mark.parametrize("model", [DataFlowManager, DataFlowManagerFL])
def test_method(model):
  df = wrap_to_cl(model(64, 32, 64, 4, 2, 1))
  df.reset()

  # simulate add x2, x1, x0
  # x2 <- x1 + x0
  s1_preg = df.get_src(1)
  assert s1_preg.preg == 0
  s2_preg = df.get_src(0)
  assert s2_preg.preg == 63
  d1_preg = df.get_dst(2)
  assert d1_preg.success == 1
  assert d1_preg.preg == 31
  s1_read = df.read_tag(s1_preg.preg)
  assert s1_read.ready == 1
  assert s1_read.value == 0
  s2_read = df.read_tag(s2_preg.preg)
  assert s2_read.ready == 1
  assert s2_read.value == 0
  df.cycle()

  df.write_tag(tag=d1_preg.preg, value=0)
  df.cycle()

  df.commit_tag(d1_preg.preg)
  df.cycle()

  # simulate addi x2, x2, 42
  s1_preg = df.get_src(2)
  assert s1_preg.preg == 31
  d1_preg = df.get_dst(2)
  assert d1_preg.success == 1
  assert d1_preg.preg == 1
  s1_read = df.read_tag(s1_preg.preg)
  assert s1_read.ready == 1
  assert s1_read.value == 0
  df.cycle()

  df.write_tag(tag=d1_preg.preg, value=42)
  df.cycle()

  df.commit_tag(d1_preg.preg)
  df.cycle()


def test_state_machine():
  run_test_state_machine(DataFlowManager, DataFlowManagerFL,
                         (64, 32, 64, 4, 2, 1))