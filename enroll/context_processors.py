
def login_form(request):
    if hasattr(request, 'login_form'):
        return dict(login_form=request.login_form)
    return {}