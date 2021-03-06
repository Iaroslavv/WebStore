from flask_admin.contrib.sqla import ModelView
from flask_security import current_user
from flask import abort, redirect, request, url_for


# Create customized model view class
class AccessView(ModelView):
    def is_accessible(self):
        return (
            current_user.is_authenticated and
            current_user.is_active and current_user.has_role("admin")
        )

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            # access denied
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('security.login', next=request.url))
