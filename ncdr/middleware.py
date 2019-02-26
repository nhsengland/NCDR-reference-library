from .models import Version


def latest_version(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        assert hasattr(request, "session"), (
            "The latest_version middleware requires Authentication middleware "
            "to be installed. Edit your MIDDLEWARE setting to insert "
            "'django.contrib.auth.middleware.AuthenticationMiddleware' before "
            "'ncdr.middleware.latest_version'."
        )

        if request.user.is_authenticated and request.user.current_version:
            version = request.user.current_version
        else:
            version = Version.latest_published()

        request.version = version

        return get_response(request)

    return middleware
