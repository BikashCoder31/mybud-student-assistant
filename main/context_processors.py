from django.conf import settings


def identity(request):
    return {"mybud_mode": settings.MYBUD_MODE, "maintainer": "Bikash Kushwaha"}
