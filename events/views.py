from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser, Event, Registration
from .forms import EventForm, ProfileUpdateForm

# USER REGISTRATION
def register_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")
        profile_image = request.FILES.get("profile_image")

        # Check if username already exists
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Choose another.")
            return redirect("register")

        # Create user
        user = CustomUser.objects.create_user(username=username, password=password, role=role)
        
        if profile_image:
            user.profile_image = profile_image
            user.save()

        login(request, user)
        messages.success(request, "Registration successful!")
        return redirect("my_account")

    return render(request, "register.html")

# USER LOGIN
def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("my_account")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "login.html")

# USER LOGOUT
@login_required
def logout_user(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")

# CREATE EVENT
@login_required
def create_event(request):
    if request.user.role == "student":
        messages.error(request, "Students are not allowed to create events.")
        return redirect("home")

    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, "Event created successfully!")
            return redirect("home")
    else:
        form = EventForm()

    return render(request, "create_event.html", {"form": form})

# DISPLAY EVENTS
def event_list(request):
    events = Event.objects.filter(is_approved=True)
    return render(request, "home.html", {"events": events, "user": request.user})

# REGISTER FOR EVENT
@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Check if user has already registered
    if Registration.objects.filter(event=event, student=request.user).exists():
        messages.warning(request, "You have already registered for this event.")
        return render(request, "register_event.html", {
            "event": event,
            "user": request.user
        })
    
    if request.method == "POST":
        # Create registration
        registration = Registration.objects.create(
            event=event,
            student=request.user
        )
        
        messages.success(request, "Successfully registered for the event!")
        return redirect("home")
    
    # Render the registration form template
    return render(request, "register_event.html", {
        "event": event,
        "user": request.user
    })

# USER ACCOUNT
@login_required
def my_account(request):
    return render(request, "profile.html", {"user": request.user})

# EDIT PROFILE
@login_required
def edit_profile(request):
    user = request.user

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            # Save the form directly since we're using ModelForm
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("my_account")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileUpdateForm(instance=user)

    return render(request, "edit_profile.html", {"form": form})


# DELETE PROFILE
@login_required
def delete_profile(request):
    user = request.user
    logout(request)
    user.delete()
    messages.info(request, "Your account has been deleted.")
    return redirect("home")
