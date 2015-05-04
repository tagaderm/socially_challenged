from django.conf.urls import patterns, url

from s_network import views

urlpatterns = patterns('',

    url(r'^$', views.home, name='home'),
    url(r'^register', views.register, name='register'),
    url(r'^login', views.user_login, name='login'),
    url(r'^logout', views.logout, name='logout'),
    url(r'^failed_fb_login', views.failed_fb_login, name='failed_fb_login'),

    url(r'^insert_photo', views.insert_photo, name='insert_photo'),
    url(r'^update_profile_pic/$', views.update_profile_pic, name='update_profile_pic'),
    url(r'^update_profile/$', views.update_profile, name='update_profile'),

    url(r'^newpost', views.new_wall_post, name='new_wall_post'),
    url(r'^delete_post', views.delete_wall_post, name='delete_wall_post'),
    url(r'^newcomment', views.new_comment, name='new_comment'),
    url(r'^delete_comment', views.delete_comment, name='delete_comment'),
    url(r'^(?P<username>\w+)/see_all_posts', views.see_all_posts, name='see_all_posts'),

    url(r'^\w+/user_search/$', views.user_search, name='user_search'),
    url(r'^\w+/search_results/$', views.search_results, name='search_results'),

    url(r'^(?P<username>\w+)/$', views.profile, name='profile'),
    url(r'^(?P<username>\w+)/upload_pics/$', views.upload_pics, name='upload_pics'),
    url(r'^(?P<username>\w+)/photos/$', views.photo_album, name='photos'),
    url(r'^(?P<username>\w+)/edit_profile/$', views.edit_profile, name='edit_profile'),
    url(r'^(?P<username>\w+)/info/$', views.info, name='info'),
    url(r'^(?P<username>\w+)/choose_profile_pic/$', views.choose_profile_pic, name='choose_pic'),
)
