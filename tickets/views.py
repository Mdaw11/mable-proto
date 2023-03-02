from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Ticket, TicketHistory, Attachment, Category, Message
from .forms import TicketForm
from projects.models import Project
from users.models import CustomUser
from notifications.models import Notification

# Create your views here.
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    tickets = Ticket.objects.filter(
        Q(category__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    
    
    context = {'tickets': tickets}
    
    return render(request, 'dashboard/dashboard.html', context)

def get_ticket_data(request):
    high_priority = Ticket.objects.filter(priority='High').count()
    medium_priority = Ticket.objects.filter(priority='Medium').count()
    low_priority = Ticket.objects.filter(priority='Low').count()
    none_priority = Ticket.objects.filter(priority='None').count()
    
    data = {
        'values': [high_priority, medium_priority, low_priority, none_priority]
    }
    
    return JsonResponse(data)


def get_type_data(request):
    misc_type = Ticket.objects.filter(type='Misc').count()
    bug_type = Ticket.objects.filter(type='Bug').count()
    help_type = Ticket.objects.filter(type='Help Needed').count()
    concern_type = Ticket.objects.filter(type='Concern').count()
    question_type = Ticket.objects.filter(type='Question').count()
    
    data = {
        'values': [misc_type, bug_type, help_type, concern_type, question_type]
    }
    
    return JsonResponse(data)

def get_status_data(request):
    open_status = Ticket.objects.filter(status=True).count()
    close_status = Ticket.objects.filter(status=False).count()
    
    data = {
        'values': [open_status, close_status]
    }
    
    return JsonResponse(data)


def ticket_home(request): 
    tickets = Ticket.objects.all()
    search_query = request.GET.get('search')
    
    categories = Category.objects.all()[0:5]
    ticket_count = tickets.count()
    
    
    if request.user.is_authenticated:
        user = request.user
        tickets = tickets.filter(Q(host=user) | Q(assignee=user))
    
    # Filter tickets based on a search query
    if search_query:
        tickets = tickets.filter(
            Q(host__username__icontains=search_query) | 
            Q(assignee__username__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(status__icontains=search_query) |
            Q(priority__icontains=search_query) |
            Q(type__icontains=search_query)
        )
    
    
    # Paginate the ticket table
    paginator = Paginator(tickets, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    
    context = {'tickets': tickets, 'categories': categories,
               'ticket_count': ticket_count, 'page_obj': page_obj, 
               'search_query': search_query}
    return render(request, 'tickets/ticket_home.html', context)

# Ticket detail page
def ticket(request, pk):
    ticket = Ticket.objects.get(id=pk)
    ticket_messages = ticket.message_set.all()
    ticket_history = ticket.history.all()
    ticket_attachments = ticket.attachments.all()
    
    # POST method that creates a message to leave a comment
    if request.method == 'POST':
        if 'body' in request.POST:
            # if the 'body' field is present in the POST data, create a new message
            message = Message.objects.create(
                user=request.user,
                ticket=ticket,
                body=request.POST.get('body')
            )
            ticket.participants.add(request.user)
        
        else:
            # if the 'body' field is not present, should be creating a new attachment 
            for file in request.FILES.getlist('files'):
                Attachment.objects.create(
                    file=file,
                    ticket=ticket
                )
            
        return redirect('ticket', pk=ticket.id)

    # Get the search query from the request's GET parameters
    search_query = request.GET.get('q')
    
    # Filter the results based on the search query
    if search_query:
        ticket_messages = ticket_messages.filter(Q(user__username__icontains=search_query) | 
                                                 Q(body__icontains=search_query))
        
        ticket_history = ticket_history.filter(Q(name__icontains=search_query) |
                                               Q(description__icontains=search_query) |
                                               Q(updated_by__username__icontains=search_query))
        
        ticket_attachments = ticket_attachments.filter(Q(file__icontains=search_query) |
                                                Q(created__icontains=search_query))
    
    # Set the number of items you want to display on each page
    messages_per_page = 5
    history_per_page = 5
    attachments_per_page = 5
    
    # Create a paginator object for each queryset
    messages_paginator = Paginator(ticket_messages, messages_per_page)
    history_paginator = Paginator(ticket_history, history_per_page)
    attachments_paginator = Paginator(ticket_attachments, attachments_per_page)

    # Get the current page number from the request's GET parameters 
    messages_page_number = request.GET.get('messages_page')
    history_page_number = request.GET.get('history_page')
    attachments_page_number = request.GET.get('attachments_page')

    # Get the current page object for each queryset
    messages_page_obj = messages_paginator.get_page(messages_page_number)
    history_page_obj = history_paginator.get_page(history_page_number)
    attachments_page_obj = attachments_paginator.get_page(attachments_page_number)
    
    
    context = {
        'ticket': ticket, 
        'ticket_messages': messages_page_obj, 
        'ticket_history': history_page_obj,
        'ticket_attachments': attachments_page_obj,
        'search_query': search_query,
    }
    return render(request, 'tickets/ticket.html', context)

@login_required
def createTicket(request):
    form = TicketForm()
    
    categories = Category.objects.all()
    users = CustomUser.objects.all()
    if request.method == 'POST':
        category_name = request.POST.get('category')
        category, created = Category.objects.get_or_create(name=category_name)
        
        # Retrieve the project object that the ticket should be connected with
        project_id = request.POST.get('project')
        project = Project.objects.get(id=project_id)
        
        # Retrieve the list of selected users from the form
        assignee_ids = request.POST.getlist('assignee')
        assignee = CustomUser.objects.filter(id__in=assignee_ids)
        
        ticket = Ticket.objects.create(
            host = request.user,
            category=category,
            project=project,
            name=request.POST.get('name'),
            status=request.POST.get('status'),
            priority=request.POST.get('priority'),
            type=request.POST.get('type'),
            description=request.POST.get('description'),
        )
        
        # Add the selected users to the ticket
        ticket.assignee.set(assignee)
        
        return redirect('ticket', pk=ticket.id)
    
    context = {'form': form, 'categories': categories, 'users': users}
    return render(request, 'tickets/ticket_form.html', context)

@login_required
def updateTicket(request, pk):
    ticket = Ticket.objects.get(id=pk)
    form = TicketForm(instance=ticket)
    categories = Category.objects.all()
    if request.user != ticket.host:
        return HttpResponse('You are not allowed')
    
    if request.method == 'POST':
        category_name = request.POST.get('category')
        category, created = Category.objects.get_or_create(name=category_name)
        
        # create ticket history
        history = TicketHistory(
            ticket=ticket,
            updated_by=request.user,
            name=ticket.name,
            status=ticket.status,
            priority=ticket.priority,
            type=ticket.type,
            description=ticket.description,
        )
        history.save()

        ticket.name = request.POST.get('name')
        ticket.category = category
        ticket.status = request.POST.get('status')
        ticket.priority = request.POST.get('priority')
        ticket.type = request.POST.get('type')
        ticket.description = request.POST.get('description')
        ticket.save()
        
        return redirect('ticket', pk=ticket.id)
    
    context = {'form': form, 'ticket': ticket, 'categories': categories}
    return render(request, 'tickets/ticket_form.html', context)

@login_required
def deleteTicket(request, pk):
    ticket = Ticket.objects.get(id=pk)
    
    if request.user != ticket.host:
        return HttpResponse('You are not allowed')
    
    if request.method == 'POST':
        ticket.delete()
        return redirect('home')
    return render(request, 'tickets/ticket-delete.html', {'obj': ticket})

@login_required
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    
    if request.user != message.user:
        return HttpResponse('You are not allowed')
    
    if request.method == 'POST':
        message.delete()
        return redirect(request, 'tickets/delete.html', {'obj': message})
    
def categoriesPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    categories = Category.objects.filter(name__icontains=q)
    return render(request, 'projects/categories.html', {'categories': categories})

def activityPage(request):
    ticket_messages = Message.objects.all()
    return render(request, 'projects/activity.html', {'ticket_messages': ticket_messages})