from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Project
from django.core.paginator import Paginator
from .forms import ProjectForm
from django.db.models import Q
from tickets.models import Ticket

# Create your views here.
def project_home(request):
    projects = Project.objects.all()
    search_query = request.GET.get('search')
    if search_query:    
        projects = Project.objects.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
    )
    
        
    
    paginator = Paginator(projects, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'projects': projects, 
               'page_obj': page_obj, 
               'search_query': search_query}
    return render(request, 'projects/project_home.html', context)

def project(request, pk):
    projects = Project.objects.get(id=pk)
    search_query = request.GET.get('search')
    tickets = Ticket.objects.filter(project=projects)
    
    if request.method == 'POST':
        return redirect('project', pk=project.id)
    
    # Search functionality
    if search_query:
        tickets = tickets.filter(
            
            Q(assignee__username__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(status__iexact=search_query) |
            Q(priority__icontains=search_query) |
            Q(type__icontains=search_query)
        )
    
    # Paginate the ticket table
    paginator = Paginator(tickets, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'projects': projects, 
               'tickets': tickets,
               'page_obj': page_obj,
               'search_query': search_query}
    
    return render(request, 'projects/project.html', context)

@login_required
def createProject(request):
    form = ProjectForm()
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
        
        return redirect('project-home')
        
    context = {'form': form}
    return render(request, 'projects/project_form.html', context)

@login_required
def updateProject(request, pk):
    project = Project.objects.get(id=pk)
    form = ProjectForm(instance=project)
    
    if request.method == 'POST':
        project.name = request.POST.get('name')
        project.description = request.POST.get('description')
        project.save()
        
        return redirect('project', pk=project.id)
    
    context = {'form': form, 'project': project}
    return render(request, 'projects/project_form.html', context)

@login_required
def deleteProject(request, pk):
    projects = Project.objects.get(id=pk)
    
    if request.method == 'POST':
        projects.delete()
        return redirect('project-home')
    
    return render(request, 'projects/project-delete.html', {'obj': projects})