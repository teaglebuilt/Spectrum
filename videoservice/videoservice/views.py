from django.shortcuts import render


def home(request):
    return render(request, "home.html", {})

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        print('name', 'email', 'message')
        return redirect
    return render(request, "contact.html", {})