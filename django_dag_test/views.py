# Test tree recurse view

from django.shortcuts import render_to_response
from django.template import RequestContext
from django_dag_test.models import ConcreteNode

def tree(request):
    return render_to_response('tree.html', {'dag_list': ConcreteNode.objects.all()},  context_instance=RequestContext(request))

