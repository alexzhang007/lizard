from pymtl import *
from util.test_utils import run_test_vector_sim
from util.rtl.freelist import FreeList
from test.config import test_verilog


def test_basic():
  run_test_vector_sim(
      FreeList( 4, 1, 1, False, False ), [
          ( 'alloc_ports[0].call alloc_ports[0].rdy* alloc_ports[0].index* alloc_ports[0].mask* free_ports[0].call free_ports[0].index'
          ),
          ( 1, 1, 0, 0b0001, 0, 0 ),
          ( 1, 1, 1, 0b0010, 0, 0 ),
          ( 0, 1, '?', '?', 1, 0 ),
          ( 1, 1, 0, 0b0001, 0, 0 ),
          ( 1, 1, 2, 0b0100, 0, 0 ),
          ( 1, 1, 3, 0b1000, 0, 0 ),
          ( 0, 0, '?', '?', 1, 1 ),
          ( 1, 1, 1, 0b0010, 0, 0 ),
      ],
      dump_vcd=None,
      test_verilog=test_verilog )


def test_used_initial():
  run_test_vector_sim(
      FreeList( 4, 1, 1, False, False, 2 ), [
          ( 'alloc_ports[0].call alloc_ports[0].rdy* alloc_ports[0].index* alloc_ports[0].mask* free_ports[0].call free_ports[0].index'
          ),
          ( 1, 1, 2, 0b0100, 0, 0 ),
          ( 1, 1, 3, 0b1000, 0, 0 ),
          ( 0, 0, '?', '?', 1, 0 ),
          ( 1, 1, 0, 0b0001, 0, 0 ),
          ( 0, 0, '?', '?', 0, 0 ),
      ],
      dump_vcd=None,
      test_verilog=test_verilog )


def test_reverse_free_order():
  run_test_vector_sim(
      FreeList( 2, 1, 1, False, False ), [
          ( 'alloc_ports[0].call alloc_ports[0].rdy* alloc_ports[0].index* alloc_ports[0].mask* free_ports[0].call free_ports[0].index'
          ),
          ( 1, 1, 0, 0b0001, 0, 0 ),
          ( 1, 1, 1, 0b0010, 0, 0 ),
          ( 0, 0, '?', '?', 1, 1 ),
          ( 1, 1, 1, 0b0010, 0, 0 ),
      ],
      dump_vcd=None,
      test_verilog=test_verilog )


def test_bypass():
  run_test_vector_sim(
      FreeList( 2, 1, 1, True, False ), [
          ( 'alloc_ports[0].call alloc_ports[0].rdy* alloc_ports[0].index* alloc_ports[0].mask* free_ports[0].call free_ports[0].index'
          ),
          ( 1, 1, 0, 0b0001, 0, 0 ),
          ( 1, 1, 1, 0b0010, 0, 0 ),
          ( 1, 1, 1, 0b0010, 1, 1 ),
          ( 1, 1, 0, 0b0001, 1, 0 ),
      ],
      dump_vcd=None,
      test_verilog=test_verilog )


def test_release():
  run_test_vector_sim(
      FreeList( 4, 1, 1, False, False ), [
          ( 'alloc_ports[0].call alloc_ports[0].rdy* alloc_ports[0].index* alloc_ports[0].mask* free_ports[0].call free_ports[0].index release_port.call release_port.mask'
          ),
          ( 1, 1, 0, 0b0001, 0, 0, 0, 0b0000 ),
          ( 1, 1, 1, 0b0010, 0, 0, 0, 0b0000 ),
          ( 1, 1, 2, 0b0100, 0, 0, 1, 0b0011 ),
          ( 1, 1, 0, 0b0001, 1, 1, 0, 0b0000 ),
          ( 1, 1, 1, 0b0010, 1, 0, 0, 0b0000 ),
      ],
      dump_vcd=None,
      test_verilog=test_verilog )