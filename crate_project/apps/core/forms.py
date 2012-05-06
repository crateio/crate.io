from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django.contrib import auth, messages
from django.contrib.auth.models import User

from account import signals
from account.forms import SignupForm
from account.models import EmailAddress, Account
from account.utils import default_redirect, user_display


class OpenIDSignupForm(SignupForm):

    template_name = "account/signup.html"
    template_name_email_confirmation_sent = "account/email_confirmation_sent.html"
    template_name_signup_closed = "account/signup_closed.html"

    redirect_field_name = "next"
    messages = {
        "email_confirmation_sent": {
            "level": messages.INFO,
            "text": _("Confirmation email sent to %(email)s.")
        },
        "logged_in": {
            "level": messages.SUCCESS,
            "text": _("Successfully logged in as %(user)s.")
        },
        "invalid_signup_code": {
            "level": messages.WARNING,
            "text": _("The code %(code)s is invalid.")
        }
    }

    def __init__(self, *args, **kwargs):
        # remember provided (validated!) OpenID to attach it to the new user
        # later.
        self.openid = kwargs.pop("openid", None)
        # pop these off since they are passed to this method but we can't
        # pass them to forms.Form.__init__
        kwargs.pop("reserved_usernames", [])
        kwargs.pop("no_duplicate_emails", False)

        super(OpenIDSignupForm, self).__init__(*args, **kwargs)

        # these fields make no sense in OpenID
        del self.fields["password"]
        del self.fields["password_confirm"]

    def save(self, request=None):
        self.request = request

        email_confirmed = False
        new_user = self.create_user(self, commit=False)
        if settings.ACCOUNT_EMAIL_CONFIRMATION_REQUIRED:
            new_user.is_active = False
        new_user.save()
        self.create_account(new_user, self)
        email_kwargs = {"primary": True}

        EmailAddress.objects.add_email(new_user, new_user.email, **email_kwargs)
        self.after_signup(new_user, self)
        if settings.ACCOUNT_EMAIL_CONFIRMATION_REQUIRED and not email_confirmed:
            response_kwargs = {
                "request": self.request,
                "template": self.template_name_email_confirmation_sent,
                "context": {
                    "email": new_user.email,
                    "success_url": self.get_success_url(),
                }
            }
            return new_user
        else:
            if self.messages.get("email_confirmation_sent") and not email_confirmed:
                messages.add_message(
                    self.request,
                    self.messages["email_confirmation_sent"]["level"],
                    self.messages["email_confirmation_sent"]["text"] % {
                        "email": self.cleaned_data["email"]
                    }
                )
            self.login_user(new_user)
            if self.messages.get("logged_in"):
                messages.add_message(
                    self.request,
                    self.messages["logged_in"]["level"],
                    self.messages["logged_in"]["text"] % {
                        "user": user_display(new_user)
                    }
                )
        return new_user

    def create_user(self, form, commit=True, **kwargs):
        user = User(**kwargs)
        username = form.cleaned_data.get("username")
        if username is None:
            username = self.generate_username(form)
        user.username = username
        user.email = form.cleaned_data["email"].strip()
        password = form.cleaned_data.get("password")
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        if commit:
            user.save()
        return user

    def create_account(self, new_user, form):
        return Account.create(request=self.request, user=new_user)

    def generate_username(self, form):
        raise NotImplementedError("Unable to generate username by default. "
            "Override SignupView.generate_username in a subclass.")

    def after_signup(self, user, form):
        signals.user_signed_up.send(sender=SignupForm, user=user, form=form)

    def login_user(self, user):
        # set backend on User object to bypass needing to call auth.authenticate
        user.backend = "django.contrib.auth.backends.ModelBackend"
        auth.login(self.request, user)
        self.request.session.set_expiry(0)

    def get_success_url(self):
        return default_redirect(self.request, settings.ACCOUNT_SIGNUP_REDIRECT_URL)
