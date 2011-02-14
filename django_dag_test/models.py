from django.db import models

from django_dag.models import *
# Create your models here.


class ConcreteNode(node_factory('ConcreteEdge')):
    """
    Test node, adds just one field
    """
    name = models.CharField(max_length = 32)

class ConcreteEdge (edge_factory('ConcreteNode', concrete = False)):
    """
    Test edge, adds just one field
    """
    name = models.CharField(max_length = 32, blank = True, null = True)
