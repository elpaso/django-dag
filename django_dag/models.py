"""
A class to model hierarchies of objects following
Directed Acyclic Graph structure.

Some ideas stolen from: from https://github.com/stdbrouw/django-treebeard-dag

"""


from django.db import models
from django.core.exceptions import ValidationError


class NodeNotReachableException (Exception):
    """
    Exception for node distance and path
    """
    pass


class NodeBase(object):
    """
    Main node abstract model
    """

    class Meta:
        ordering = ('-id',)

    def __unicode__(self):
        return "# %s" % self.pk

    def __str__(self):
        return self.__unicode__()

    def add_child(self, descendant, **kwargs):
        """
        Adds a child
        """
        args = kwargs
        args.update({'parent' : self, 'child' : descendant })
        cls = self.children.through(**kwargs)
        return cls.save()


    def add_parent(self, parent, *args, **kwargs):
        """
        Adds a parent
        """
        return parent.add_child(self, **kwargs)

    def remove_child(self, descendant):
        """
        Removes a child
        """
        self.children.through.objects.get(parent = self, child = descendant).delete()

    def remove_parent(self, parent):
        """
        Removes a parent
        """
        parent.children.through.objects.get(parent = parent, child = self).delete()

    def parents(self):
        """
        Returns all elements which have 'self' as a direct descendant
        """
        return self.__class__.objects.filter(children = self)

    def descendants_tree(self):
        """
        Returns a tree-like structure with progeny
        """
        tree = {}
        for f in self.children.all():
            tree[f] = f.descendants_tree()
        return tree

    def ancestors_tree(self):
        """
        Returns a tree-like structure with ancestors
        """
        tree = {}
        for f in self.parents():
            tree[f] = f.ancestors_tree()
        return tree

    def descendants_set(self):
        """
        Returns a set of descendants
        """
        res = set()
        for f in self.children.all():
            res.add(f)
            res.update(f.descendants_set())
        return res

    def ancestors_set(self):
        """
        Returns a set of ancestors
        """
        res = set()
        for f in self.parents():
            res.add(f)
            res.update(f.ancestors_set())
        return res

    def distance(self, target):
        """
        Returns the shortest hops count to the target vertex
        """
        return len(self.path(target))

    def path(self, target):
        """
        Returns the shortest path
        """
        if self == target:
            return []
        if target in self.children.all():
            return [target]
        if target in self.descendants_set():
            path = None
            for d in self.children.all():
                try:
                    desc_path = d.path(target)
                    if not path or len(desc_path) < path:
                        path = [d] + desc_path
                except NodeNotReachableException:
                    pass
        else:
            raise NodeNotReachableException
        return path

    def is_root(self):
        """
        Check if has children and not ancestors
        """
        return bool(self.children.count() and not self.ancestors_set())

    def is_leaf(self):
        """
        Check if has ancestors and not children
        """
        return bool(self.ancestors_set() and not self.children.count())

    def is_island(self):
        """
        Check if has no ancestors nor children
        """
        return bool(not self.is_root() and not self.is_leaf())

    def _get_roots(self, at):
        """
        Works on objects: no queries
        """
        if not at:
          return set([self])
        roots = set()
        for a2 in at:
            roots.update(a2._get_roots(at[a2]))
        return roots

    def get_roots(self):
        """
        Returns roots nodes, if any
        """
        at =  self.ancestors_tree()
        roots = set()
        for a in at:
            roots.update(a._get_roots(at[a]))
        return roots

    def _get_leaves(self, dt):
        """
        Works on objects: no queries
        """
        if not dt:
          return set([self])
        leaves = set()
        for d2 in dt:
            leaves.update(d2._get_leaves(dt[d2]))
        return leaves

    def get_leaves(self):
        """
        Returns leaves nodes, if any
        """
        dt =  self.descendants_tree()
        leaves = set()
        for d in dt:
            leaves.update(d._get_leaves(dt[d]))
        return leaves


    @staticmethod
    def circular_checker(parent, child):
        """
        Checks that the object is not an ancestor or a descendant,
        avoid self links
        """
        if parent == child:
            raise ValidationError('Self links are not allowed')
        if child in parent.ancestors_set():
            raise ValidationError('The object is an ancestor.')
        if child in parent.descendants_set():
            raise ValidationError('The object is a descendant.')



def edge_factory(node_model, child_to_field = "id", parent_to_field = "id", concrete = True, base_model = models.Model):
    """
    Dag Edge factory
    """
    if isinstance(node_model, str):
        try:
            node_model_name = node_model.split('.')[1]
        except IndexError:
            node_model_name = node_model
    else:
        node_model_name = node_mode._meta.module_name

    class Edge(base_model):
        class Meta:
            abstract = not concrete

        parent = models.ForeignKey(node_model, related_name = "%s_child" % node_model_name, to_field = parent_to_field)
        child = models.ForeignKey(node_model, related_name = "%s_parent" % node_model_name, to_field = child_to_field)

        def __unicode__(self):
            return "%s is child of %s" % (self.child, self.parent)

        def save(self, *args, **kwargs):
            self.parent.__class__.circular_checker(self.parent, self.child)
            super(Edge, self).save(*args, **kwargs) # Call the "real" save() method.

    return Edge

def node_factory(edge_model, children_null = True, base_model = models.Model):
    """
    Dag Node factory
    """
    class Node(base_model, NodeBase):
        class Meta:
            abstract        = True

        children  = models.ManyToManyField(
                'self',
                null        = children_null,
                blank       = children_null,
                symmetrical = False,
                through     = edge_model)

    return Node

