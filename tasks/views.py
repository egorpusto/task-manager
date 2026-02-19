from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import TaskForm
from .models import Tag, Task


class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"
    paginate_by = 9

    def get_queryset(self):
        queryset = (
            Task.objects.filter(user=self.request.user)
            .prefetch_related("tags")
            .select_related("user")
        )

        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        priority = self.request.GET.get("priority")
        if priority:
            queryset = queryset.filter(priority=priority)

        tag = self.request.GET.get("tag")
        if tag:
            queryset = queryset.filter(tags__id=tag)

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        context["current_filters"] = self.request.GET
        context["now"] = timezone.now()
        return context


class TaskCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("task_list")
    success_message = 'Task "%(title)s" created successfully!'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TaskUpdateView(
    LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView
):
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("task_list")
    success_message = 'Task "%(title)s" updated successfully!'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def test_func(self):
        return self.get_object().user == self.request.user


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    success_url = reverse_lazy("task_list")
    template_name = "tasks/task_confirm_delete.html"

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def test_func(self):
        return self.get_object().user == self.request.user

    def form_valid(self, form):
        messages.success(self.request, f'Task "{self.get_object().title}" deleted.')
        return super().form_valid(form)
