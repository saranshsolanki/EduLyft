from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.login_view, name='login_view'),
    url(r'^dashboard', views.dashboard, name='dashboard'),
    url(r'^performance-tracker', views.performance_tracker, name='performance_tracker'),
    url(r'^cohort', views.cohort_page, name='cohort-page'),
    url(r'^get_cohort', views.get_cohort, name='get_cohort'),
    url(r'^logout_action', views.logout_action, name='logout'),
    url(r'^testdetail/(?P<test_id>[0-9]+)/$', views.detail_test_view, name='detail-test-view'),
    url(r'^chapterdetail/(?P<chapter_name>\w+)/$', views.detail_test_view, name='detail-test-view'),
    
    
    
    
)