from django.shortcuts import render


def inicio(request):
    return render(request, "principal/inicio.html")


def servicios(request):
    return render(request, "principal/servicios.html")