import logging

from django.contrib.auth import logout, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.views.generic import RedirectView, FormView, CreateView, ListView, TemplateView
from tasks.forms import UserSignupForm, TasksHistoryDataForm
from tasks.models import TasksHistory, TasksHistoryData, CustomUser, TasksHistoryStatus, Task
from tasks.tokens import account_activation_token
from tasks.utility import get_default_task, assign_task, process_data, get_new_task, get_user_experiences_data, \
    send_confirmation_mail, get_assigned_task_history, get_task_history

logger = logging.getLogger(__name__)


class HomePageView(TemplateView):
    template_name = 'tasks/home_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task'] = get_default_task()
        return context

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            user = self.request.user
            task_history = get_assigned_task_history(user)
            if task_history is not None:
                return redirect('tasks:Taskboard', task_id=task_history.task.id)
            else:
                new_task = get_new_task(user)
                if new_task is not None:
                    assign_task(user, new_task)
                    return redirect('tasks:Taskboard', task_id=new_task.id)
                else:
                    logger.info("No more task available. Please add more task for the user.")
                    return redirect('tasks:UpcomingTask')
        return super(HomePageView, self).dispatch(request, *args, **kwargs)


class TasksListView(ListView):
    template_name ='tasks/tasks_list.html'
    model =Task


class UpcomingTaskView(TemplateView):
    template_name = 'tasks/upcoming_task.html'


class SignUpView(SuccessMessageMixin, CreateView):
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('tasks:HomePage')
    form_class = UserSignupForm
    success_message = "Your profile was created successfully. Please confirm your email address to complete " \
                      "the registration."

    def form_valid(self, form):
        response = super().form_valid(form)  # We are using create view, and it automatically saves the data
        user = CustomUser.objects.get(username=form.cleaned_data.get('username'))
        user.is_active = False  # Deactivate account till it is confirmed
        user.save()
        try:
            send_confirmation_mail(self.request, user)
        except Exception as e:
            logger.warning("Error while signing up "+str(e))
            user.delete()
            self.success_message = None
            raise e
        return response


class ActivateAccount(RedirectView, SuccessMessageMixin):
    success_message = 'Your account have been confirmed.'
    url = reverse_lazy('tasks:HomePage')

    def get_redirect_url(self, *args, **kwargs):
        try:
            uid = force_bytes(urlsafe_base64_decode(self.kwargs['uidb64']))
            user = CustomUser.objects.get(pk=uid)
            if account_activation_token.check_token(user, self.kwargs['token']):
                user.is_active = True
                user.save()
                login(self.request, user)
                return super().get_redirect_url(*args, **kwargs)
            else:
                raise ValueError("Invalid token")
        except Exception as e:
            logger.error("Error while activating account with following exception: " + str(e))
            self.success_message = None
            raise e


class TaskView(LoginRequiredMixin, TemplateView):
    template_name = 'tasks/task_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        task_id = self.kwargs['task_id']
        task_history = get_task_history(user, task_id)
        if task_history is not None:
            context['task_history'] = task_history
            context['task'] = task_history.task
            context['is_task_assigned'] = True if (task_history.status == TasksHistoryStatus.ASSIGNED.value) else False
        else:
            logger.error(f"{user}\'s task status is not assigned or completed. Please assign the task to user.")
            context['task_history'] = None

        return context


class SubmitDataView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    template_name = 'tasks/submit_data.html'
    form_class = TasksHistoryDataForm
    success_url = reverse_lazy('tasks:MyExperiences', kwargs={'page_number': 1})
    success_message = "Your experience is saved successfully"

    def form_valid(self, form):
        task_history = TasksHistory.objects.get(id=self.kwargs['task_history_id'])
        try:
            process_data(form, task_history)
        except Exception as e:
            logger.error("Problem while saving data. following exception occurred: " + str(e))
            self.success_message = "Your data is not saved. Please retry."
        return super().form_valid(form)


class MyExperienceView(LoginRequiredMixin, ListView):
    template_name = 'tasks/my_experiences.html'
    paginate_by = 5
    context_object_name = 'task_history_data_list'

    def get_queryset(self):
        return TasksHistoryData.objects.select_related('task_history').filter(task_history__user=self.request.user). \
            order_by('-task_history_id')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        task_history_data_list = context['task_history_data_list']
        context['user_experiences'] = get_user_experiences_data(task_history_data_list)
        return context


class LogoutView(LoginRequiredMixin, RedirectView):
    """
    A view that logout user and redirect to homepage.
    """
    permanent = True
    query_string = False
    url = reverse_lazy('tasks:HomePage')

    def get_redirect_url(self, *args, **kwargs):
        """
        Logout user and redirect to target url.
        """
        logout(self.request)
        return super(LogoutView, self).get_redirect_url(*args, **kwargs)


class PrivacyPolicyView(TemplateView):
    template_name = 'tasks/privacy_policy.html'


class TermsOfUseView(TemplateView):
    template_name = 'tasks/terms_of_use.html'


class AboutUsPageView(TemplateView):
    template_name = 'tasks/about_us.html'
