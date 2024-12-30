class UserTypeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if hasattr(request.user, 'is_doctor') and request.user.is_doctor:
                request.user_type = 'doctor'
            else:
                request.user_type = 'patient'
        return self.get_response(request)
