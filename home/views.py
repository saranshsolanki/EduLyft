from django.shortcuts import render

# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext


def home(request):
    if request.method == 'GET':
        return render_to_response('home/home.html', context_instance=RequestContext(request))