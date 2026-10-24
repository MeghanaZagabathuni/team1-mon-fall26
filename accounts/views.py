from django.shortcuts import render, redirect
from .forms import SignUpForm
from .models import AccountProfile
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            AccountProfile.objects.create(
                user=user,
                role=form.cleaned_data["account_type"],
            )

            login(request, user)
            return redirect("signup_success")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


@login_required
def signup_success_view(request):
    profile = request.user.account_profile

    return render(
        request,
        "accounts/signup_success.html",
        {
            "first_name": request.user.first_name or request.user.username,
            "is_caregiver": profile.role == "caregiver",
        },
    )
