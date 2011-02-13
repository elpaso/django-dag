Django DAG
----------

Django-dag is a small reusable app which implements a Directed Acyclic Graph.

Usage
.....

Django-dag uses abstract base classes, to use it you must create your own
concrete classes that inherit from Django-dag classes.

The `dag_test` app contains a simple example and a unit test to show
you its usage.

Example::

    class ConcreteNode(node_factory('ConcreteEdge')):
        """
        Test node, adds just one field
        """
        name = models.CharField(max_length = 32)

    class ConcreteEdge (edge_factory(ConcreteNode, concrete = False)):
        """
        Test edge, adds just one field
        """
        name = models.CharField(max_length = 32, blank = True, null = True)