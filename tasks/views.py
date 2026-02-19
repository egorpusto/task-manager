from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.forms import CustomUserCreationForm

from .filters import TaskFilter
from .forms import TaskForm
from .models import Tag, Task


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("task_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


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
        self.filterset = TaskFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        context["tags"] = Tag.objects.all()
        context["current_filters"] = self.filterset.data
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


class TaskUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("task_list")
    success_message = 'Task "%(title)s" updated successfully!'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy("task_list")
    template_name = "tasks/task_confirm_delete.html"

    def get_queryset(self):
        return Task.objects.select_related("user").filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, f'Task "{self.object.title}" deleted.')
        return super().form_valid(form)
