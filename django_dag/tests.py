
from django.test import TestCase
from django_dag.models import *


# Test classes

class ConcreteNode(node_factory('ConcreteEdge')):
    """
    Test node, adds just one field
    """
    name = models.CharField(max_length = 32)

    class Meta:
        app_label = 'django_dag'

class ConcreteEdge(edge_factory('ConcreteNode', concrete = False)):
    """
    Test edge, adds just one field
    """
    name = models.CharField(max_length = 32, blank = True, null = True)

    class Meta:
        app_label = 'django_dag'


class DagTestCase(TestCase):

    def setUp(self):
        for i in range(1,11):
            ConcreteNode(name = "%s" % i).save()


    def test_01_objects_were_created(self):
        for i in range(1,11):
            self.assertEqual(ConcreteNode.objects.get(name="%s" % i).name, "%s" % i)


    def test_02_dag(self):
        # Get nodes
        for i in range(1,11):
            globals()["p%s" % i] = ConcreteNode.objects.get(pk=i)

        # Creates a DAG
        #from IPython import embed; embed()
        p1.add_child(p5)
        p5.add_child(p7)

        tree = p1.descendants_tree()
        # {<ConcreteNode: # 5>: {<ConcreteNode: # 7>: {}}}
        self.assertEqual(tree.keys()[0], p5)
        self.assertEqual(tree.values()[0].keys()[0], p7)
        self.assertEqual(tree[tree.keys()[0]].values()[0], {})

        l=[p.pk for p in p1.descendants_set()]
        l.sort()
        self.assertEqual(l, [5, 7])

        p1.add_child(p6)
        p2.add_child(p6)
        p3.add_child(p7)
        p6.add_child(p7)
        p6.add_child(p8)
        l=[p.pk for p in p2.descendants_set()]
        l.sort()
        self.assertEqual(l, [6, 7, 8])

        # ValidationError: [u'The object is a descendant.']
        self.assertRaises(ValidationError, p2.add_child, p8)

        try:
            p2.add_child(p8)
        except ValidationError, e:
            self.assertEqual(unicode(e[0]), u'The object is a descendant.')

        # Checks that p8 was not added two times
        l=[p.pk for p in p2.descendants_set()]
        l.sort()
        self.assertEqual(l, [6, 7, 8])

        p6.add_parent(p4)
        p9.add_parent(p3)
        p9.add_parent(p6)
        self.assertRaises(ValidationError, p9.add_child, p2)
        try:
            p9.add_child(p2)
        except ValidationError, e:
            self.assertEqual(unicode(e[0]), u'The object is an ancestor.')

        self.assertEqual(str(p1.descendants_tree()), """{<ConcreteNode: # 5>: {<ConcreteNode: # 7>: {}}, <ConcreteNode: # 6>: {<ConcreteNode: # 8>: {}, <ConcreteNode: # 9>: {}, <ConcreteNode: # 7>: {}}}""")
        l=[p.pk for p in p1.descendants_set()]
        l.sort()
        self.assertEqual(l, [5, 6, 7, 8, 9])
        self.assertEqual(p1.distance(p8), 2)

        #Test additional fields for edge
        p9.add_child(p10, name = 'test_name')
        self.assertEqual(p9.children.through.objects.filter(child=p10)[0].name, u'test_name')

        self.assertEqual(str(p1.path(p7)), '[<ConcreteNode: # 6>, <ConcreteNode: # 7>]')
        self.assertEqual(str(p1.path(p10)), '[<ConcreteNode: # 6>, <ConcreteNode: # 9>, <ConcreteNode: # 10>]')
        self.assertEqual(p1.distance(p7), 2)

        self.assertEqual(str(p1.get_leaves()), 'set([<ConcreteNode: # 8>, <ConcreteNode: # 10>, <ConcreteNode: # 7>])')
        self.assertEqual(str(p8.get_roots()), 'set([<ConcreteNode: # 1>, <ConcreteNode: # 2>, <ConcreteNode: # 4>])')

        self.assertTrue(p1.is_root())
        self.assertFalse(p1.is_leaf())
        self.assertFalse(p10.is_root())
        self.assertTrue(p10.is_leaf())
        self.assertFalse(p6.is_leaf())
        self.assertFalse(p6.is_root())

        self.assertRaises(ValidationError, p6.add_child, p6)
        try:
            p6.add_child(p6)
        except ValidationError, e:
            self.assertEqual(unicode(e[0]), u'Self links are not allowed.')

        # Remove a link and test island
        p10.remove_parent(p9)
        self.assertFalse(p10 in p9.descendants_set())
        self.assertTrue(p10.is_island())

        self.assertEqual(str(p6.ancestors_set()), 'set([<ConcreteNode: # 1>, <ConcreteNode: # 2>, <ConcreteNode: # 4>])')

        p1.remove_child(p6)
        self.assertEqual(str(p6.ancestors_set()), 'set([<ConcreteNode: # 2>, <ConcreteNode: # 4>])')

        self.assertFalse(p1 in p6.ancestors_set())

        # Testing the view
        from django.shortcuts import render_to_response
        response = str(render_to_response('tree.html', { 'dag_list': ConcreteNode.objects.all()}))
        self.assertEqual(response, """Content-Type: text/html; charset=utf-8\r\n\r\n# 1\nDescendants:\n# 5\n# 7\n\n\n\n# 2\nDescendants:\n# 6\n# 8\n\n# 9\n\n# 7\n\n\n\n# 3\nDescendants:\n# 9\n\n# 7\n\n\n# 4\nDescendants:\n# 6\n# 8\n\n# 9\n\n# 7\n\n\n\n# 5\n\n# 6\n\n# 7\n\nAncestors:\n# 3\n\n# 5\n# 1\n\n\n# 6\n# 2\n\n# 4\n\n\n# 8\n\nAncestors:\n# 6\n# 2\n\n# 4\n\n\n# 9\n\nAncestors:\n# 3\n\n# 6\n# 2\n\n# 4\n\n\n# 10\n\n\n""")
        
