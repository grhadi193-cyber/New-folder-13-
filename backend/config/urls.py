import os
from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse, FileResponse, Http404
from ninja import NinjaAPI

api = NinjaAPI(title="Shop API", version="1.0.0", docs_url="/docs")

# -- Routers ------------------------------------------------------------------
from core.api            import router as core_router
from accounts.api        import router as accounts_router
from store.api           import router as store_router
from shipping.api        import router as shipping_router
from payment.api         import router as payment_router
from blog.api            import router as blog_router
from admin_panel.api     import router as admin_router
from notifications.api   import router as notifications_router

api.add_router("/",             core_router)
api.add_router("/auth",         accounts_router)
api.add_router("/",             store_router)
api.add_router("/shipping",     shipping_router)
api.add_router("/payment",      payment_router)
api.add_router("/blog",         blog_router)
api.add_router("/admin",        admin_router)
api.add_router("/notifications", notifications_router)


def health_check(request):
    return JsonResponse({"status": "ok"})


def serve_media(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.isfile(file_path):
        return FileResponse(open(file_path, "rb"))
    raise Http404


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health", health_check),
    path("api/",   api.urls),
    re_path(r"^public/media/(?P<path>.+)$", serve_media),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    try:
        from django.urls import include
        import debug_toolbar
        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
