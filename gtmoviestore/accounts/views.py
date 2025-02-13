from django.shortcuts import render
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from .forms import CustomUserCreationForm, CustomErrorList
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import secrets
from django.core.mail import send_mail
from django.shortcuts import HttpResponse, redirect
from django.urls import reverse
from django.contrib.auth.models import User

# Create your views here.
# Temporary token storage
reset_tokens = {}

def request_password_reset(request):
    if request.method == "POST":
        email = request.POST.get("email")

        # Generate a unique token
        token = secrets.token_urlsafe(20)
        reset_tokens[token] = email  # Store the token temporarily

        # Create reset link
        reset_link = request.build_absolute_uri(reverse("reset_password", args=[token]))

        # Send the email
        send_mail(
            "Password Reset Request",
            f"Click the link to reset your password: {reset_link}",
            "gatechmoviestore@gmail.com",
            [email],
            fail_silently=False,
        )

        return HttpResponse("An email has been sent with the reset link.")

    # 🛠️ FIXED: Manually insert CSRF token using JavaScript
    return HttpResponse("""
        <html>
            <head>
                <title>Reset Password</title>
                <script>
                    function getCSRFToken() {
                        return document.cookie.split('; ')
                            .find(row => row.startsWith('csrftoken='))
                            ?.split('=')[1];
                    }
                </script>
            </head>
            <body>
                <h2>Forgot Your Password?</h2>
                <p>Enter your email, and we'll send you a reset link.</p>
                <form method="POST">
                    <input type="hidden" name="csrfmiddlewaretoken" id="csrf_token">
                    <input type="email" name="email" placeholder="Enter your email" required>
                    <button type="submit">Send Reset Link</button>
                </form>
                <script>
                    document.getElementById("csrf_token").value = getCSRFToken();
                </script>
            </body>
        </html>
    """)

def reset_password(request, token):
    email = reset_tokens.get(token)

    if not email:
        return HttpResponse("Invalid or expired reset link.")

    if request.method == "POST":
        username = request.POST.get("username")
        new_password = request.POST.get("new_password")

        # Find the user by username
        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            del reset_tokens[token]  # Remove token after use
            return HttpResponse("Password has been reset. You can now log in.")
        except User.DoesNotExist:
            return HttpResponse("No user found with that username.")

    # 🛠️ FIXED: Use f-string to safely insert token
    html_content = f"""
        <html>
            <head>
                <title>Reset Password</title>
                <script>
                    function getCSRFToken() {{
                        let csrfCookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
                        return csrfCookie ? csrfCookie.split('=')[1] : "";
                    }}
                </script>
            </head>
            <body>
                <h2>Reset Your Password</h2>
                <p>Enter your username and a new password.</p>

                <form method="POST">
                    <input type="hidden" name="csrfmiddlewaretoken" id="csrf_token">
                    <input type="hidden" name="token" value="{token}">
                    <p>
                        <label for="username">Username:</label>
                        <input id="username" type="text" name="username" required>
                    </p>
                    <p>
                        <label for="new_password">New Password:</label>
                        <input id="new_password" type="password" name="new_password" required>
                    </p>
                    <button type="submit">Reset Password</button>
                </form>

                <script>
                    document.getElementById("csrf_token").value = getCSRFToken();
                </script>
            </body>
        </html>
    """

    return HttpResponse(html_content)



@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')

def orders(request):
    template_data = {}
    template_data['title'] = 'Orders'
    template_data['orders'] = request.user.order_set.all()
    return render(request, 'accounts/orders.html',
        {'template_data': template_data})

def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html', {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(
            request,
            username = request.POST['username'],
            password = request.POST['password']
        )
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html',
                {'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect('home.index')

def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            form.save()
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html', {'template_data': template_data})

