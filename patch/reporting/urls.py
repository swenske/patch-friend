from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^advisories/$', views.AdvisoryIndexView.as_view(), name='advisory_list'),
    url(r'^advisories/(?P<slug>[-\w]+)/$', views.AdvisoryDetailView.as_view(), name='advisory_detail'),
]