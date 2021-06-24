from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.
from .models import *
from .forms import CustomerCreateForm
brand = 'DONGJIN VIETNAM'
