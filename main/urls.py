from functools import partial

from django.urls import path

from . import views

urlpatterns = [
    path("", views.page, name="home"),
    path("health/", views.health, name="health"),
    path("api/expenses/", views.expenses_api, name="expenses_api"),
]
for name in ("chat", "code", "recipe", "travel", "expenses"):
    urlpatterns.append(
        path(f"{name}/", partial(views.page, template=f"{name}.html"), name=f"{name}_page")
    )
for task in ("chat", "code", "recipes", "travel", "detect-food"):
    urlpatterns.append(path(f"api/{task}/", partial(views.tool_api, task=task), name=f"{task}_api"))
