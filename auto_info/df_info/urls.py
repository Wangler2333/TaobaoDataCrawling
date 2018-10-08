
from django.conf.urls import url
from df_info import views

urlpatterns = [
    url(r'code$', views.code_deal),
]
