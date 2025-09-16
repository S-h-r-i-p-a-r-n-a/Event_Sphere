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
    
    if event.is_approved:
        if not Registration.objects.filter(event=event, student=request.user).exists():
            Registration.objects.create(event=event, student=request.user)
            messages.success(request, "Successfully registered for the event!")
        else:
            messages.warning(request, "You have already registered for this event.")
    
    return redirect("home")

# USER ACCOUNT
@login_required
def my_account(request):
    return render(request, "profile.html", {"user": request.user})

# EDIT PROFILE
@login_required
def edit_profile(request):
    user = request.user  # Get the logged-in user

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            new_username = form.cleaned_data.get("username").strip()

            # 🔹 Check if username exists (excluding the logged-in user)
            if CustomUser.objects.filter(username=new_username).exclude(id=user.id).exists():
                messages.error(request, "Username already taken. Choose another one.")
                return render(request, "edit_profile.html", {"form": form})

            # 🔹 Update only changed fields
            updated_fields = []
            if user.username != new_username:
                user.username = new_username
                updated_fields.append("username")
            if "profile_image" in form.cleaned_data and form.cleaned_data["profile_image"]:
                user.profile_image = form.cleaned_data["profile_image"]
                updated_fields.append("profile_image")
            if user.first_name != form.cleaned_data["first_name"]:
                user.first_name = form.cleaned_data["first_name"]
                updated_fields.append("first_name")
            if user.last_name != form.cleaned_data["last_name"]:
                user.last_name = form.cleaned_data["last_name"]
                updated_fields.append("last_name")
            if user.email != form.cleaned_data["email"]:
                user.email = form.cleaned_data["email"]
                updated_fields.append("email")
            if user.college_name != form.cleaned_data["college_name"]:
                user.college_name = form.cleaned_data["college_name"]
                updated_fields.append("college_name")
            if user.role != form.cleaned_data["role"]:
                user.role = form.cleaned_data["role"]
                updated_fields.append("role")

            if updated_fields:
                user.save(update_fields=updated_fields)  # Save only updated fields
            
            messages.success(request, "Profile updated successfully!")
            return redirect("my_account")  # Redirect to profile page

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = ProfileUpdateForm(instance=user)  # Pre-fill form with current user data

    return render(request, "edit_profile.html", {"form": form})  # Ensure a response is returned


# DELETE PROFILE
@login_required
def delete_profile(request):
    user = request.user
    logout(request)
    user.delete()
    messages.info(request, "Your account has been deleted.")
    return redirect("home")
