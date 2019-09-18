
from django.db.models import CharField
from django_dag.models import node_factory, edge_factory


class ConcreteNode(node_factory('ConcreteEdge')):
    """
    Test node, adds just one field
    """
    name = CharField(max_length=32)

    def __str__(self):
        return '# %s' % self.name

    class Meta:
        app_label = 'django_dag'


class ConcreteEdge(edge_factory('ConcreteNode', concrete=False)):
    """
    Test edge, adds just one field
    """
    name = CharField(max_length=32, blank=True, null=True)

    class Meta:
        app_label = 'django_dag'


