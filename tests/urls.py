from django.conf.urls import patterns, url, include
import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.index, name='index'),
    url(r'^create', views.create, name='create'),
    url(r'^upload_student_marks',  view=views.upload_student_marks, name='upload_student_marks'),
    url(r'^upload_marks_final',  view=views.upload_marks_final, name='upload_marks_final'),
    url(r'get_tests/', views.get_all_tests, name='get_tests'),
    url(r'get_subjects/', views.get_subjects, name='get_subjects'),
    url(r'get_chapters/', views.get_chapters, name='get_chapters'),
    url(r'get_students/', views.get_students, name='get_students'),
    
    
    
)