"""
Unit tests for django-dag
"""


__test__ = {"doctest": """

>>> from dag_test.models import ConcreteNode
>>> for i in range(1,11):
...     ConcreteNode(name = "%s" % i).save()

>>> for i in range(1,11):
...     vars()["p%s" % i] = ConcreteNode.objects.get(pk=i)

>>> p1.add_child(p5)
>>> p5.add_child(p7)
>>> p1.descendants_tree()
{<ConcreteNode: # 5>: {<ConcreteNode: # 7>: {}}}

>>> l=[p.pk for p in p1.descendants_set()]
>>> l.sort()
>>> l
[5, 7]


>>> p1.add_child(p6)
>>> p2.add_child(p6)
>>> p3.add_child(p7)
>>> p6.add_child(p7)
>>> p6.add_child(p8)

>>> l=[p.pk for p in p2.descendants_set()]
>>> l.sort()
>>> l
[6, 7, 8]

>>> p2.add_child(p8)
Traceback (most recent call last):
    ...
ValidationError: [u'The object is a descendant.']

Checks that p8 was not added two times

>>> l=[p.pk for p in p2.descendants_set()]
>>> l.sort()
>>> l
[6, 7, 8]


>>> p6.add_parent(p4)
>>> p9.add_parent(p3)
>>> p9.add_parent(p6)
>>> p9.add_child(p2)
Traceback (most recent call last):
    ...
ValidationError: [u'The object is an ancestor.']

>>> p1.descendants_tree()
{<ConcreteNode: # 5>: {<ConcreteNode: # 7>: {}}, <ConcreteNode: # 6>: {<ConcreteNode: # 8>: {}, <ConcreteNode: # 9>: {}, <ConcreteNode: # 7>: {}}}

>>> l=[p.pk for p in p1.descendants_set()]
>>> l.sort()
>>> l
[5, 6, 7, 8, 9]

>>> p1.distance(p8)
2

Test additional fields for edge

>>> p9.add_child(p10, name = 'test_name')
>>> p9.children.through.objects.filter(child=p10)[0].name
u'test_name'

>>> p1.path(p7)
[<ConcreteNode: # 6>, <ConcreteNode: # 7>]

>>> p1.path(p10)
[<ConcreteNode: # 6>, <ConcreteNode: # 9>, <ConcreteNode: # 10>]

>>> p1.distance(p7)
2

>>> p1.get_leaves()
set([<ConcreteNode: # 8>, <ConcreteNode: # 10>, <ConcreteNode: # 7>])


>>> p8.get_roots()
set([<ConcreteNode: # 1>, <ConcreteNode: # 2>, <ConcreteNode: # 4>])

>>> p1.is_root()
True

>>> p1.is_leaf()
False

>>> p10.is_root()
False

>>> p10.is_leaf()
True

>>> p6.is_root()
False

>>> p6.is_leaf()
False

>>> p6.add_child(p6)
Traceback (most recent call last):
    ...
ValidationError: [u'Self links are not allowed']

"""}

