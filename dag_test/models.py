from django.db import models

from dag.models import *
# Create your models here.


class ConcreteNode(node_factory('ConcreteEdge')):
    """
    Test
    """
    name = models.CharField(max_length = 32)

class ConcreteEdge (edge_factory(ConcreteNode, concrete = False)):
    """
    No new fields
    """
    name = models.CharField(max_length = 32, blank = True, null = True)