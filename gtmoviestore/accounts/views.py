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

        return HttpResponse("""
            <html>
                <head>
                    <title>Password Reset Requested</title>
                    <link rel="stylesheet" href="/static/css/style.css">
                </head>
                <body>
                    <div class="p-3 mt-4">
                        <div class="container">
                            <div class="row justify-content-center">
                                <div class="col-md-8">
                                    <div class="card shadow p-3 mb-4 rounded">
                                        <div class="card-body text-center">
                                            <h2>Reset Link Sent</h2>
                                            <hr />
                                            <p>If the email exists, a password reset link has been sent.</p>
                                            <a href="/accounts/login/" class="btn bg-dark text-white">Back to Login</a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </body>
            </html>
        """)

    return HttpResponse("""
        <html>
            <head>
                <title>Reset Password</title>
                <link rel="stylesheet" href="/static/css/style.css">
            </head>
            <body>
                <div class="p-3 mt-4">
                    <div class="container">
                        <div class="row justify-content-center">
                            <div class="col-md-8">
                                <div class="card shadow p-3 mb-4 rounded">
                                    <div class="card-body">
                                        <h2>Forgot Your Password?</h2>
                                        <hr />
                                        <p>Enter your email, and we'll send you a reset link.</p>
                                        <form method="POST">
                                            <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                                            <p>
                                                <label for="email">Email</label>
                                                <input id="email" type="email" name="email" required class="form-control">
                                            </p>
                                            <div class="text-center">
                                                <button type="submit" class="btn bg-dark text-white">Send Reset Link</button>
                                            </div>
                                        </form>
                                        <div class="text-center mt-3">
                                            <a href="/accounts/login/" class="text-primary">Back to Login</a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <script>
                    document.querySelector("[name='csrfmiddlewaretoken']").value = document.cookie.split('; ')
                        .find(row => row.startsWith('csrftoken='))
                        ?.split('=')[1] || "";
                </script>
            </body>
        </html>
    """.replace("{csrf_token}", request.COOKIES.get("csrftoken", "")))

def reset_password(request, token):
    email = reset_tokens.get(token)

    if not email:
        return HttpResponse("""
            <html>
                <head>
                    <title>Invalid Reset Link</title>
                    <link rel="stylesheet" href="/static/css/style.css">
                </head>
                <body>
                    <div class="p-3 mt-4">
                        <div class="container">
                            <div class="row justify-content-center">
                                <div class="col-md-8">
                                    <div class="card shadow p-3 mb-4 rounded">
                                        <div class="card-body text-center">
                                            <h2>Invalid or Expired Reset Link</h2>
                                            <hr />
                                            <p>Please request a new password reset.</p>
                                            <a href="/accounts/password_reset/" class="btn bg-dark text-white">Try Again</a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </body>
            </html>
        """)

    if request.method == "POST":
        username = request.POST.get("username")
        new_password = request.POST.get("new_password")

        # Find the user by username
        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            del reset_tokens[token]  # Remove token after use
            return HttpResponse("""
                <html>
                    <head>
                        <title>Password Reset Successful</title>
                        <link rel="stylesheet" href="/static/css/style.css">
                    </head>
                    <body>
                        <div class="p-3 mt-4">
                            <div class="container">
                                <div class="row justify-content-center">
                                    <div class="col-md-8">
                                        <div class="card shadow p-3 mb-4 rounded">
                                            <div class="card-body text-center">
                                                <h2>Password Reset Successfully</h2>
                                                <hr />
                                                <p>You can now log in with your new password.</p>
                                                <a href="/accounts/login/" class="btn bg-dark text-white">Go to Login</a>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </body>
                </html>
            """)
        except User.DoesNotExist:
            return HttpResponse("""
                <html>
                    <head>
                        <title>Reset Failed</title>
                        <link rel="stylesheet" href="/static/css/style.css">
                    </head>
                    <body>
                        <div class="p-3 mt-4">
                            <div class="container">
                                <div class="row justify-content-center">
                                    <div class="col-md-8">
                                        <div class="card shadow p-3 mb-4 rounded">
                                            <div class="card-body text-center">
                                                <h2>No User Found</h2>
                                                <hr />
                                                <p>The username you entered does not exist.</p>
                                                <a href="/accounts/password_reset/" class="btn bg-dark text-white">Try Again</a>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </body>
                </html>
            """)

    return HttpResponse(f"""
        <html>
            <head>
                <title>Reset Password</title>
                <link rel="stylesheet" href="/static/css/style.css">
            </head>
            <body>
                <div class="p-3 mt-4">
                    <div class="container">
                        <div class="row justify-content-center">
                            <div class="col-md-8">
                                <div class="card shadow p-3 mb-4 rounded">
                                    <div class="card-body">
                                        <h2>Reset Your Password</h2>
                                        <hr />
                                        <p>Enter your username and a new password.</p>

                                        <form method="POST">
                                            <input type="hidden" name="csrfmiddlewaretoken" id="csrf_token">
                                            <p>
                                                <label for="username">Username:</label>
                                                <input id="username" type="text" name="username" required class="form-control">
                                            </p>
                                            <p>
                                                <label for="new_password">New Password:</label>
                                                <input id="new_password" type="password" name="new_password" required class="form-control">
                                            </p>
                                            <div class="text-center">
                                                <button type="submit" class="btn bg-dark text-white">Reset Password</button>
                                            </div>
                                        </form>
                                        <div class="text-center mt-3">
                                            <a href="/accounts/login/" class="text-primary">Back to Login</a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
        </html>
    """)



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

