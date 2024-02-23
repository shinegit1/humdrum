from django.contrib.auth.views import LoginView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetView, \
    PasswordResetCompleteView
from django.urls import path, reverse_lazy
 
from tasks.forms import LoginForm
from tasks.views import HomePageView, TaskView, SignUpView, LogoutView, SubmitDataView, MyExperienceView, \
    ActivateAccount, UpcomingTaskView, PrivacyPolicyView, TermsOfUseView, AboutUsPageView, TasksListView

app_name = "tasks"

urlpatterns = [
    path('', HomePageView.as_view(), name='HomePage'),
    path('challenge-list/', TasksListView.as_view(), name='TaskList'),
    path('challenge/<int:task_id>/', TaskView.as_view(), name='Taskboard'),
    path('upcoming-challenge/', UpcomingTaskView.as_view(), name='UpcomingTask'),
    path('submit-data/<int:task_history_id>/', SubmitDataView.as_view(), name='SubmitData'),
    path('login/', LoginView.as_view(template_name='accounts/login.html', form_class=LoginForm), name='LoginPage'),
    path('my-experiences/<int:page_number>/', MyExperienceView.as_view(), name='MyExperiences'),
    path('signup/', SignUpView.as_view(), name='SignupPage'),
    path('logout/', LogoutView.as_view(), name='LogoutPage'),
    path('account-activate/<uidb64>/<token>/', ActivateAccount.as_view(), name='ActivatePage'),
    path('password_reset/', PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url=reverse_lazy("tasks:password_reset_done")),
        name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(
        template_name="accounts/password_reset_done.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name="accounts/password_reset_confirm.html",
        success_url=reverse_lazy("tasks:password_reset_complete")), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'), name="password_reset_complete"),
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='PrivacyPolicy'),
    path('terms-of-use/', TermsOfUseView.as_view(), name='TermsOfUse'),
    path('about-us/', AboutUsPageView.as_view(), name='About_Us'),
]
