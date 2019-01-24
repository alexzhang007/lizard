from collections import OrderedDict
from pymtl import *
from util.rtl.method import MethodSpec
from util.toposort import toposort


class Interface( object ):
  """An interface for a hardware module.

  Represents a method-based interface to a hardware module.
  An Interface is composed of an ordered sequence of named methods,
  each of which may have multiple instances. Multiple instances
  of a given method allows multiple calls per cycle.

  All methods have a well-defined sequence, determined by the order
  in which they are added (by add_method). The side-effects and results
  of earlier methods are read by the later methods, but not vice-versa.
  In the event of multiple instances of a method, instances with lower
  indices occur before methods with higher indices.

  For example, consider a free list with a free and allocate method.
  Assume the free list is full, and in one cycle, both the free and
  allocate methods are called. If the free method precedes the allocate
  method, the free will take effect, freeing a spot, and the allocation
  will succeed. If the allocate method precedes the free method, then
  the free list will be full, the allocation will fail, and the free 
  will take effect. A successfull allocation will then be able to 
  happen the next cycle.

  These semantics allows for a precise translation between FL, CL, 
  and RTL level models. If method A precedes method B, then
  the relationship above holds in RTL. In FL and CL, in any given cycle,
  method A must be called before method B.

  An interface can be used either by the implementing model, or by a 
  client model.
  
  An implementing model uses an interface by applying it on itself
  by using interface.apply(model). That call will
  instantiate the appropriate ports for every instance of every 
  method declared in the interface as fields in the model.
  Ports for a method are generated as <method name>_<port_name>.
  Ports of array type are represented as arrays of ports.
  When a method has multiple instances (count is not None),
  all ports become arrays of ports.

  A client model, in general, needs to call an arbitray combination
  of methods defined in a variety of other interfaces.
  These outgoing method call ports are generated with require:
  interface.require(model, 'prefix', 'methodname', count=4)
  This will create ports, using the same name mangling scheme as above,
  but with the prefix 'prefix_' (note the underscore is added).
  """

  def __init__( s, spec, ordering_chains=None ):
    """Initialize the method map.

    Subclasses must call this!
    """
    """Adds a method to the interface.

    The args, rets, has_call and has_rdy are as defined by the MethodSpec
    __init__. count defines the number of instances. If None, the method
    will only have 1 instance, the ports will not be wrapped in arrays.
    If any number (including 0, or 1), then the ports will be wrapped 
    in arrays of the specified length. Note the distinction between
    1 and None: one is an array of length 1, and one is a single port
    not wrapped in an array.
    """
    names = [ method.name for method in spec ]
    if len( names ) != len( set( names ) ):
      raise ValueError( 'Duplicate methods: {}'.format( names ) )

    # Compute the ordering based on the chains
    # If no chains present, ordering is as given
    if ordering_chains is None:
      order = names
    else:
      # Construct a dependency graph from the ordering chains
      graph = { name: set() for name in names }
      for chain in ordering_chains:
        # chains only make sense if they have at least 2 elements
        assert len( chain ) >= 2
        pred = chain[ 0 ]
        for current in chain[ 1:]:
          # Every item depends on the previous item
          graph[ current ].add( pred )
          pred = current
      order = toposort( graph )

    spec_dict = { method.name: method for method in spec }
    s.methods = OrderedDict([( name, spec_dict[ name ] ) for name in order ] )

  @staticmethod
  def bypass_chain( action1, action2, action1_action2_bypass ):
    """Generates an ordering chain depending on a bypass flag.

    If the bypass flag is False, action2 happens before action1.
    If the bypass flag is True, action1 happens before action2.
    """

    if action1_action2_bypass:
      return [ action1, action2 ]
    else:
      return [ action2, action1 ]

  @staticmethod
  def successor( last, priors ):
    """Generates a list of ordering chains placing last after priors."""

    return [[ prior, last ] for prior in priors ]

  def _inject( s, target, prefix, name, spec, count, direction ):
    if count is None:
      port_map = spec.generate( direction )
    else:
      ports = [
          spec.generate( MethodSpec.DIRECTION_CALLEE ) for _ in range( count )
      ]
      port_map = {}
      for port_name in spec.ports():
        port_map[ port_name ] = [
            ports[ i ][ port_name ] for i in range( count )
        ]

    for port_name, port in port_map.iteritems():
      mangled = '{}{}_{}'.format( prefix, name, port_name )
      if hasattr( target, mangled ):
        raise ValueError( 'Mangled field already exists: {}'.format( mangled ) )
      setattr( target, mangled, port )

  def apply( s, target ):
    """Binds incoming ports to the target

    This method should be called by implementing models.
    """
    for name, spec in s.methods.iteritems():
      s._inject( target, '', name, spec, spec.count,
                 MethodSpec.DIRECTION_CALLEE )

  def require( s, target, prefix, name, count=None ):
    """Binds an outgoing port from this interface to the target

    This method should be called by client models.
    """
    if len( prefix ) > 0:
      prefix = '{}_'.format( prefix )

    spec, available = s.methods[ name ]
    # Should be possible to prevent over-allocation
    # if available is None and count is None:
    #   pass
    # elif available is not None and count is None:
    #   available -= 1
    # elif count <= available:
    #   available -= count
    # else:
    #   raise ValueError('No more ports for method left: {}'.format(name))
    s._inject( target, prefix, name, spec, count, MethodSpec.DIRECTION_CALLER )
