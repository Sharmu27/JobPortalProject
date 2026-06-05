from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Job, Application
from .forms import JobForm, ApplicationForm

def home_view(request):
    active_listings = Job.objects.filter(is_filled=False).order_by('-created_at')[:6]
    return render(request, 'jobs/home.html', {'jobs': active_listings})

def search_view(request):
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    job_type = request.GET.get('job_type', '')
    
    results = Job.objects.filter(is_filled=False)
    
    if query:
        results = results.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if location:
        results = results.filter(location__icontains=location)
    if job_type:
        results = results.filter(job_type=job_type)
        
    return render(request, 'jobs/search.html', {
        'jobs': results,
        'query': query,
        'location': location,
        'job_type': job_type
    })

@login_required
def create_job_view(request):
    if request.user.profile.user_type != 'employer':
        messages.error(request, "Only employers can list open jobs positions.")
        return redirect('home')
        
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.save()
            messages.success(request, "New vacancy listing published successfully.")
            return redirect('employer_dashboard')
    else:
        form = JobForm()
    return render(request, 'jobs/create_job.html', {'form': form})

@login_required
def edit_job_view(request, pk):
    job = get_object_or_404(Job, pk=pk, employer=request.user)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Listing parameters altered updated cleanly.")
            return redirect('employer_dashboard')
    else:
        form = JobForm(instance=job)
    return render(request, 'jobs/edit_job.html', {'form': form, 'job': job})

@login_required
def delete_job_view(request, pk):
    job = get_object_or_404(Job, pk=pk, employer=request.user)
    job.delete()
    messages.success(request, "Job listing dropped removed completely.")
    return redirect('employer_dashboard')

@login_required
def apply_view(request, pk):
    if request.user.profile.user_type != 'seeker':
        messages.error(request, "Employers cannot issue vacancy submission applications.")
        return redirect('home')
        
    job = get_object_or_404(Job, pk=pk)
    
    if Application.objects.filter(job=job, seeker=request.user).exists():
        messages.warning(request, "You already applied to this target resource tracking link.")
        return redirect('home')
        
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.seeker = request.user
            application.save()
            messages.success(request, "Application sent completely to human resources successfully.")
            return redirect('applications')
    else:
        form = ApplicationForm()
    return render(request, 'jobs/apply.html', {'form': form, 'job': job})

@login_required
def employer_dashboard(request):
    if request.user.profile.user_type != 'employer':
        return redirect('home')
    my_jobs = Job.objects.filter(employer=request.user).order_by('-created_at')
    return render(request, 'jobs/employer_dashboard.html', {'jobs': my_jobs})

@login_required
def applications_view(request):
    if request.user.profile.user_type == 'seeker':
        apps = Application.objects.filter(seeker=request.user).order_by('-applied_at')
        return render(request, 'jobs/applications.html', {'applications': apps, 'role': 'seeker'})
    else:
        apps = Application.objects.filter(job__employer=request.user).order_by('-applied_at')
        return render(request, 'jobs/applications.html', {'applications': apps, 'role': 'employer'})
