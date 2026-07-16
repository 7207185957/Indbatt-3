from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from core.mixins import SuperAdminRequiredMixin

from .forms import UnitUserChangeForm, UnitUserCreationForm
from .models import User


class UserListView(SuperAdminRequiredMixin, ListView):
    """Super Admin: list of all individual user accounts in the system."""

    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset().select_related('company').order_by('username')
        q = self.request.GET.get('q', '').strip()
        role = self.request.GET.get('role', '').strip()
        if q:
            queryset = queryset.filter(username__icontains=q)
        if role:
            queryset = queryset.filter(role=role)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['role'] = self.request.GET.get('role', '')
        context['role_choices'] = User._meta.get_field('role').choices
        return context


class UserCreateView(SuperAdminRequiredMixin, CreateView):
    """Super Admin: create a brand-new, individually-attributable login."""

    model = User
    form_class = UnitUserCreationForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"User account '{self.object.username}' created.")
        return response


class UserUpdateView(SuperAdminRequiredMixin, UpdateView):
    """Super Admin: edit role/company/details of an existing account."""

    model = User
    form_class = UnitUserChangeForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"User account '{self.object.username}' updated.")
        return response


class SetUserPasswordView(SuperAdminRequiredMixin, UpdateView):
    """Super Admin: reset another user's password (no shared credentials)."""

    model = User
    template_name = 'accounts/user_set_password.html'
    fields = []

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = SetPasswordForm(self.object)
        return render(request, self.template_name, {'form': form, 'target_user': self.object})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = SetPasswordForm(self.object, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Password updated for '{self.object.username}'.")
            return redirect('accounts:user_list')
        return render(request, self.template_name, {'form': form, 'target_user': self.object})


class MyPasswordChangeView(PasswordChangeView):
    """Any logged-in user can change their own password."""

    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('dashboard:home')

    def form_valid(self, form):
        messages.success(self.request, 'Your password has been changed.')
        return super().form_valid(form)
