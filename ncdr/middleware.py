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
        preview_mode = False

        if request.user.is_authenticated and request.user.current_version:
            version = request.user.current_version
            if not version.is_published:
                preview_mode = True
        else:
            # Unauthenticated users should get a published version too
            version = Version.objects.filter(is_published=True).latest()

        request.version = version
        request.preview_mode = preview_mode

        return get_response(request)

    return middleware
