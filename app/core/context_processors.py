def user_role_context(request):
    if request.user.is_authenticated:
        return {'user_role': request.user.user_type}
    return {'user_role': request.session.get('user_role', None)}