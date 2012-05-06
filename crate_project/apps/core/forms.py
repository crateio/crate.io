from account.forms import SignupForm

class OpenIDSignupForm(SignupForm):

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
        del self.fields["password1"]
        del self.fields["password2"]
