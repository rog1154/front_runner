from django.urls import path
from . import views

app_name = 'race_simulation'
urlpatterns = [
    path('',views.index,name='index'),
    path('simulate/<slug:id>',views.simulate,name='simulate'),
    path('race_list',views.race_list,name='race_list'),
    path('scrape_race/<slug:date>/<slug:id>',views.scrape_race,name='scrape_race'),
]