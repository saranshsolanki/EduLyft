from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.shortcuts import render, render_to_response
from django.template.context import RequestContext
from django.utils import importlib, simplejson
import json

from Students.models import StudentAnswers
from forms import LoginForm



tests_app = models.get_app("tests")

models_tests = importlib.import_module(tests_app.__name__[:-6] + "models") 


# Create your views here.
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username','')
            password = request.POST.get('password','')
            user = authenticate(username = username, password = password)
            if user is not None:
                if user.is_active:
                    login(request,user)
                    return HttpResponseRedirect('dashboard')
                else:
                    return HttpResponse("Error")
            else:
                return render_to_response('Students/login.html', {'login': form}, 
                              context_instance=RequestContext(request))
        else:
            return render_to_response('Students/login.html', {'login': form}, 
                              context_instance=RequestContext(request))
            
    elif request.method == "GET":
        form = LoginForm()
        return render_to_response('Students/login.html', {'login': form}, 
                              context_instance=RequestContext(request))

@login_required(login_url='')
def dashboard(request):
    current_user = request.user
    current_user_id = current_user.id
    latest_test = models_tests.TestPerformance.objects.filter(student_id__exact = current_user_id).latest('test__test_date')
    
    physics_score = latest_test.physics_score
    chemistry_score = latest_test.chemistry_score
    math_score = latest_test.math_score
    
    overall_score = latest_test.overall_score
    insti_rank = latest_test.insti_rank
    
    test_performance = get_all_tests_performance(current_user_id)
    
    phy_lod_easy_data = get_lod_data(current_user_id, 1, 1)
    phy_lod_medium_data = get_lod_data(current_user_id, 1, 2)
    phy_lod_difficult_data = get_lod_data(current_user_id, 1, 3)
    
    chem_lod_easy_data = get_lod_data(current_user_id, 2, 1)
    chem_lod_medium_data = get_lod_data(current_user_id, 2, 2)
    chem_lod_difficult_data = get_lod_data(current_user_id, 2, 3)
    
    math_lod_easy_data = get_lod_data(current_user_id, 3, 1)
    math_lod_medium_data = get_lod_data(current_user_id, 3, 2)
    math_lod_difficult_data = get_lod_data(current_user_id, 3, 3)
    
    phy_lod_data = []
    phy_lod_data.append({"type":"Easy","total":phy_lod_easy_data[0],"attempted":phy_lod_easy_data[1],
                         "correct":phy_lod_easy_data[2]})
    phy_lod_data.append({"type":"Medium","total":phy_lod_medium_data[0],"attempted":phy_lod_medium_data[1],
                         "correct":phy_lod_medium_data[2]})
    phy_lod_data.append({"type":"Difficult","total":phy_lod_difficult_data[0],"attempted":phy_lod_difficult_data[1],
                         "correct":phy_lod_difficult_data[2]})
    
    chem_lod_data = []
    chem_lod_data.append({"type":"Easy","total":chem_lod_easy_data[0],"attempted":chem_lod_easy_data[1],
                         "correct":chem_lod_easy_data[2]})
    chem_lod_data.append({"type":"Medium","total":chem_lod_medium_data[0],"attempted":chem_lod_medium_data[1],
                         "correct":chem_lod_medium_data[2]})
    chem_lod_data.append({"type":"Difficult","total":chem_lod_difficult_data[0],"attempted":chem_lod_difficult_data[1],
                         "correct":chem_lod_difficult_data[2]})
    
    math_lod_data = []
    math_lod_data.append({"type":"Easy","total":math_lod_easy_data[0],"attempted":math_lod_easy_data[1],
                         "correct":math_lod_easy_data[2]})
    math_lod_data.append({"type":"Medium","total":math_lod_medium_data[0],"attempted":math_lod_medium_data[1],
                         "correct":math_lod_medium_data[2]})
    math_lod_data.append({"type":"Difficult","total":math_lod_difficult_data[0],"attempted":math_lod_difficult_data[1],
                         "correct":math_lod_difficult_data[2]})
    
    phy_toq_single_data = get_toq_data(current_user_id, 1, 1)
    phy_toq_multiple_data = get_toq_data(current_user_id, 1, 2)
    phy_toq_integer_data = get_toq_data(current_user_id, 1, 3)
    
    phy_toq_data = []
    phy_toq_data.append({"type":"Single Correct","total":phy_toq_single_data[0],"attempted":phy_toq_single_data[1],
                         "correct":phy_toq_single_data[2]})
    phy_toq_data.append({"type":"Multi Correct","total":phy_toq_multiple_data[0],"attempted":phy_toq_multiple_data[1],
                         "correct":phy_toq_multiple_data[2]})
    phy_toq_data.append({"type":"Integer","total":phy_toq_integer_data[0],"attempted":phy_toq_integer_data[1],
                         "correct":phy_toq_integer_data[2]})
    
    chem_toq_single_data = get_toq_data(current_user_id, 2, 1)
    chem_toq_multiple_data = get_toq_data(current_user_id, 2, 2)
    chem_toq_integer_data = get_toq_data(current_user_id, 2, 3)
    
    chem_toq_data = []
    chem_toq_data.append({"type":"Single Correct","total":chem_toq_single_data[0],"attempted":chem_toq_single_data[1],
                         "correct":chem_toq_single_data[2]})
    chem_toq_data.append({"type":"Multi Correct","total":chem_toq_multiple_data[0],"attempted":chem_toq_multiple_data[1],
                         "correct":chem_toq_multiple_data[2]})
    chem_toq_data.append({"type":"Integer","total":chem_toq_integer_data[0],"attempted":chem_toq_integer_data[1],
                         "correct":chem_toq_integer_data[2]})
    
    math_toq_single_data = get_toq_data(current_user_id, 3, 1)
    math_toq_multiple_data = get_toq_data(current_user_id, 3, 2)
    math_toq_integer_data = get_toq_data(current_user_id, 3, 3)
    
    math_toq_data = []
    math_toq_data.append({"type":"Single Correct","total":math_toq_single_data[0],"attempted":math_toq_single_data[1],
                         "correct":math_toq_single_data[2]})
    math_toq_data.append({"type":"Multi Correct","total":math_toq_multiple_data[0],"attempted":math_toq_multiple_data[1],
                         "correct":math_toq_multiple_data[2]})
    math_toq_data.append({"type":"Integer","total":math_toq_integer_data[0],"attempted":math_toq_integer_data[1],
                         "correct":math_toq_integer_data[2]})
        
    temp_json = {}
    
    temp_json["overall_score"] = overall_score
    temp_json["physics_score"] = physics_score
    temp_json["chemistry_score"] = chemistry_score
    temp_json["math_score"] = math_score
    temp_json["insti_rank"] = insti_rank
    temp_json["tests_performance"] = simplejson.dumps(test_performance)
    temp_json["phy_lod_data"] = simplejson.dumps(phy_lod_data)
    temp_json["chem_lod_data"] = simplejson.dumps(chem_lod_data)
    temp_json["math_lod_data"] = simplejson.dumps(math_lod_data)
    temp_json["phy_toq_data"] = simplejson.dumps(phy_toq_data)
    temp_json["chem_toq_data"] = simplejson.dumps(chem_toq_data)
    temp_json["math_toq_data"] = simplejson.dumps(math_toq_data)
    
    return render_to_response('Students/dashboard.html',temp_json,
                              context_instance=RequestContext(request))

@login_required(login_url='')
def detail_test_view(request, test_id):
    current_user = request.user
    current_user_id = current_user.id
    
    test_instance = models_tests.Tests.objects.get(id = test_id)
    
    student_test_performance = models_tests.TestPerformance.objects.get(student_id__exact = current_user_id, 
                                                                           test_id__exact = test_id)
    physics_score = student_test_performance.physics_score
    chemistry_score = student_test_performance.chemistry_score
    math_score = student_test_performance.math_score
    
    overall_score = student_test_performance.overall_score
    insti_rank = student_test_performance.insti_rank
    
    student_responses = get_studentanswers_for_test(test_id, current_user_id)
    chapters_performance = get_chapter_performance_for_test(test_id,current_user_id)
    
    phy_lod_easy_data = get_test_lod_data(current_user_id, 1, 1,test_id)
    phy_lod_medium_data = get_test_lod_data(current_user_id, 1, 2, test_id)
    phy_lod_difficult_data = get_test_lod_data(current_user_id, 1, 3, test_id)
    
    chem_lod_easy_data = get_test_lod_data(current_user_id, 2, 1, test_id)
    chem_lod_medium_data = get_test_lod_data(current_user_id, 2, 2, test_id)
    chem_lod_difficult_data = get_test_lod_data(current_user_id, 2, 3, test_id)
    
    math_lod_easy_data = get_test_lod_data(current_user_id, 3, 1, test_id)
    math_lod_medium_data = get_test_lod_data(current_user_id, 3, 2, test_id)
    math_lod_difficult_data = get_test_lod_data(current_user_id, 3, 3, test_id)
    
    phy_lod_data = []
    phy_lod_data.append({"type":"Easy","total":phy_lod_easy_data[0],"attempted":phy_lod_easy_data[1],
                         "correct":phy_lod_easy_data[2]})
    phy_lod_data.append({"type":"Medium","total":phy_lod_medium_data[0],"attempted":phy_lod_medium_data[1],
                         "correct":phy_lod_medium_data[2]})
    phy_lod_data.append({"type":"Difficult","total":phy_lod_difficult_data[0],"attempted":phy_lod_difficult_data[1],
                         "correct":phy_lod_difficult_data[2]})
    
    chem_lod_data = []
    chem_lod_data.append({"type":"Easy","total":chem_lod_easy_data[0],"attempted":chem_lod_easy_data[1],
                         "correct":chem_lod_easy_data[2]})
    chem_lod_data.append({"type":"Medium","total":chem_lod_medium_data[0],"attempted":chem_lod_medium_data[1],
                         "correct":chem_lod_medium_data[2]})
    chem_lod_data.append({"type":"Difficult","total":chem_lod_difficult_data[0],"attempted":chem_lod_difficult_data[1],
                         "correct":chem_lod_difficult_data[2]})
    
    math_lod_data = []
    math_lod_data.append({"type":"Easy","total":math_lod_easy_data[0],"attempted":math_lod_easy_data[1],
                         "correct":math_lod_easy_data[2]})
    math_lod_data.append({"type":"Medium","total":math_lod_medium_data[0],"attempted":math_lod_medium_data[1],
                         "correct":math_lod_medium_data[2]})
    math_lod_data.append({"type":"Difficult","total":math_lod_difficult_data[0],"attempted":math_lod_difficult_data[1],
                         "correct":math_lod_difficult_data[2]})
    
    phy_toq_single_data = get_test_toq_data(current_user_id, 1, 1, test_id)
    phy_toq_multiple_data = get_test_toq_data(current_user_id, 1, 2, test_id)
    phy_toq_integer_data = get_test_toq_data(current_user_id, 1, 3, test_id)
    
    phy_toq_data = []
    phy_toq_data.append({"type":"Single Correct","total":phy_toq_single_data[0],"attempted":phy_toq_single_data[1],
                         "correct":phy_toq_single_data[2]})
    phy_toq_data.append({"type":"Multi Correct","total":phy_toq_multiple_data[0],"attempted":phy_toq_multiple_data[1],
                         "correct":phy_toq_multiple_data[2]})
    phy_toq_data.append({"type":"Integer","total":phy_toq_integer_data[0],"attempted":phy_toq_integer_data[1],
                         "correct":phy_toq_integer_data[2]})
    
    chem_toq_single_data = get_toq_data(current_user_id, 2, 1)
    chem_toq_multiple_data = get_toq_data(current_user_id, 2, 2)
    chem_toq_integer_data = get_toq_data(current_user_id, 2, 3)
    
    chem_toq_data = []
    chem_toq_data.append({"type":"Single Correct","total":chem_toq_single_data[0],"attempted":chem_toq_single_data[1],
                         "correct":chem_toq_single_data[2]})
    chem_toq_data.append({"type":"Multi Correct","total":chem_toq_multiple_data[0],"attempted":chem_toq_multiple_data[1],
                         "correct":chem_toq_multiple_data[2]})
    chem_toq_data.append({"type":"Integer","total":chem_toq_integer_data[0],"attempted":chem_toq_integer_data[1],
                         "correct":chem_toq_integer_data[2]})
    
    math_toq_single_data = get_toq_data(current_user_id, 3, 1)
    math_toq_multiple_data = get_toq_data(current_user_id, 3, 2)
    math_toq_integer_data = get_toq_data(current_user_id, 3, 3)
    
    math_toq_data = []
    math_toq_data.append({"type":"Single Correct","total":math_toq_single_data[0],"attempted":math_toq_single_data[1],
                         "correct":math_toq_single_data[2]})
    math_toq_data.append({"type":"Multi Correct","total":math_toq_multiple_data[0],"attempted":math_toq_multiple_data[1],
                         "correct":math_toq_multiple_data[2]})
    math_toq_data.append({"type":"Integer","total":math_toq_integer_data[0],"attempted":math_toq_integer_data[1],
                         "correct":math_toq_integer_data[2]})
    
    temp_json = {}
    temp_json["test_id"] = test_instance.id
    temp_json["test_name"] = test_instance.name
    temp_json["test_date"] = test_instance.test_date
    temp_json["no_of_questions"] = test_instance.no_of_questions
    temp_json["overall_score"] = overall_score
    temp_json["physics_score"] = physics_score
    temp_json["chemistry_score"] = chemistry_score
    temp_json["math_score"] = math_score
    temp_json["insti_rank"] = insti_rank
    temp_json["detailed_student_response"] = simplejson.dumps(student_responses)
    temp_json["chapters_performance"] = simplejson.dumps(chapters_performance)
    temp_json["phy_lod_data"] = simplejson.dumps(phy_lod_data)
    temp_json["chem_lod_data"] = simplejson.dumps(chem_lod_data)
    temp_json["math_lod_data"] = simplejson.dumps(math_lod_data)
    temp_json["phy_toq_data"] = simplejson.dumps(phy_toq_data)
    temp_json["chem_toq_data"] = simplejson.dumps(chem_toq_data)
    temp_json["math_toq_data"] = simplejson.dumps(math_toq_data)
    
    return render_to_response('Students/detail_test_view.html',temp_json,
                              context_instance=RequestContext(request))
    
@login_required(login_url='')
def detail_chapter_view(request, chapter_name):
    current_user = request.user
    current_user_id = current_user.id
    
    chapter = models_tests.ChaptersList.objects.get(name__iexact = chapter_name)
    
    total_answers = StudentAnswers.objects.filter(student_id = current_user_id, 
                                                  question__chapter = chapter).count()
    attempted_answers = StudentAnswers.objects.filter(student_id = current_user_id, is_answered = True, 
                                                  question__chapter = chapter).count()
    correct_answers = StudentAnswers.objects.filter(student_id = current_user_id, is_correct = True, 
                                                  question__chapter = chapter).count()
    wrong_answers = attempted_answers - correct_answers
    
    temp_json = {}
    temp_json["total_answers"] = total_answers
    temp_json["attempted_answers"] = attempted_answers
    temp_json["correct_answers"] = correct_answers
    temp_json["wrong_answers"] = wrong_answers
    
    return render_to_response('Students/detail_test_view.html',temp_json,
                              context_instance=RequestContext(request))

@login_required(login_url='')
def performance_tracker(request):
    current_user = request.user
    current_user_id = current_user.id
    test_performance = get_all_tests_performance(current_user_id)
    chapter_list = get_all_chapters_for_student(current_user_id)
    
    temp_json = {}
    temp_json["tests_performance"] = simplejson.dumps(test_performance)
    temp_json["chapters_list"] = chapter_list
    
    return render_to_response('Students/performance_tracker.html',temp_json,
                              context_instance=RequestContext(request))
    

@login_required(login_url='')
def cohort_page(request):
    current_user = request.user
    current_user_id = current_user.id
    
    temp_json = {}
    
    return render_to_response('Students/cohort.html',temp_json,
                              context_instance=RequestContext(request))
    
def get_all_tests_performance(student_id):
    tests_performance = models_tests.TestPerformance.objects.filter(student_id__exact = student_id).order_by('-test__test_date')
    
    tests=[]
    for test in tests_performance:
        temp_dict={}
        temp_dict["test_name"] = test.test.name
        temp_dict["test_id"] = test.test.id
        temp_dict["physics_score"] = test.physics_score
        temp_dict["chemistry_score"] = test.chemistry_score
        temp_dict["math_score"] = test.math_score
        temp_dict["overall_score"] = test.overall_score
        temp_dict["insti_rank"] = test.insti_rank
        temp_dict["test_date"] = test.test.test_date.isoformat()
        
        tests.append(temp_dict)
    
    return tests

def get_lod_data(student_id,subject_id,lod_type):
    total_answers = StudentAnswers.objects.filter(student_id__exact = student_id, 
                                                  question__subject__exact = subject_id,
                                                  question__lod__exact = lod_type).count()
    attempted_answers = StudentAnswers.objects.filter(student_id__exact = student_id, is_answered =True,
                                                      question__subject__exact = subject_id,
                                                      question__lod__exact = lod_type).count()
    correct_answers = StudentAnswers.objects.filter(student_id__exact = student_id, is_answered =True, 
                                                    is_correct=True, question__subject__exact = subject_id,
                                                    question__lod__exact = lod_type).count()
    
    data = [total_answers,attempted_answers,correct_answers]
    return data

def get_test_lod_data(student_id,subject_id,lod_type,test_id):
    total_answers = StudentAnswers.objects.filter(student_id__exact = student_id,
                                                  question__test__exact = test_id,
                                                  question__subject__exact = subject_id,
                                                  question__lod__exact = lod_type).count()
    attempted_answers = StudentAnswers.objects.filter(student_id__exact = student_id, is_answered =True,
                                                      question__test__exact = test_id,
                                                      question__subject__exact = subject_id,
                                                      question__lod__exact = lod_type).count()
    correct_answers = StudentAnswers.objects.filter(student_id__exact = student_id, is_answered =True,
                                                    question__test__exact = test_id, is_correct=True, 
                                                    question__subject__exact = subject_id,
                                                    question__lod__exact = lod_type).count()
    
    data = [total_answers,attempted_answers,correct_answers]
    return data

def get_toq_data(student_id,subject_id,toq_type):
    total_answers = StudentAnswers.objects.filter(student_id__exact = student_id, 
                                                  question__subject__exact = subject_id,
                                                  question__type__exact = toq_type).count()
    attempted_answers = StudentAnswers.objects.filter(student_id__exact = student_id, is_answered =True,
                                                      question__subject__exact = subject_id,
                                                      question__type__exact = toq_type).count()
    correct_answers = StudentAnswers.objects.filter(student_id__exact = student_id, is_answered =True, 
                                                    is_correct=True, question__subject__exact = subject_id,
                                                    question__type__exact = toq_type).count()
    
    data = [total_answers,attempted_answers,correct_answers]
    return data

def get_test_toq_data(student_id,subject_id,toq_type,test_id):
    total_answers = StudentAnswers.objects.filter(student_id__exact = student_id,
                                                  question__test__exact = test_id, 
                                                  question__subject__exact = subject_id,
                                                  question__type__exact = toq_type).count()
    attempted_answers = StudentAnswers.objects.filter(student_id__exact = student_id, is_answered =True,
                                                      question__test__exact = test_id,
                                                      question__subject__exact = subject_id,
                                                      question__type__exact = toq_type).count()
    correct_answers = StudentAnswers.objects.filter(student_id__exact = student_id, is_answered =True,
                                                    question__test__exact = test_id, is_correct=True, 
                                                    question__subject__exact = subject_id,
                                                    question__type__exact = toq_type).count()
    
    data = [total_answers,attempted_answers,correct_answers]
    return data
    
#return only those chapters which appears in test a student has taken
def get_all_chapters_for_student(student_id):
    tests_performance = models_tests.TestPerformance.objects.filter(student_id__exact = student_id).order_by('-test__test_date')
    tests=[]
    for test in tests_performance:
        tests.append(test.test.id)
    
    chapters_dict = []
    temp_dict = {"Physics":[],"Chemistry":[],"Mathematics":[]}
        
    for test in tests:
        test_instance = models_tests.Tests.objects.get(id = test)
        questions = test_instance.questions_set.all()
        physics_chapters = temp_dict["Physics"]
        chem_chapters = temp_dict["Chemistry"]
        math_chapters = temp_dict["Mathematics"]
        for question in questions:
            chapter_name = question.chapter.name
            if question.subject.name == "Physics":
                if chapter_name not in physics_chapters:
                    physics_chapters.append(chapter_name)
            elif question.subject.name == "Chemistry":
                if chapter_name not in chem_chapters:
                    chem_chapters.append(chapter_name)
            elif question.subject.name == "Mathematics":
                if chapter_name not in math_chapters:
                    math_chapters.append(chapter_name)
    
    chapters_dict.append(temp_dict)
    return temp_dict
             
    
def get_studentanswers_for_test(test_id, student_id):
    student_answers = StudentAnswers.objects.filter(student_id__exact = student_id, 
                                                    question__test__exact = test_id)
    answers=[]
    for answer in student_answers:
        temp_dict={}
        temp_dict["question_no"] = answer.question.question_no
        temp_dict["chapter"] = answer.question.chapter.name
        temp_dict["attempt_ans"] = answer.attempt_ans
        temp_dict["score"] = answer.score
        temp_dict["answer"] = answer.question.answer
        
        
        answers.append(temp_dict)
    
    return answers

def get_chapter_performance_for_test(test_id,student_id):
    test = models_tests.Tests.objects.get(id=test_id)
    questions = test.questions_set.all()
    
    chapters = []
    for question in questions:
        chapter_id = question.chapter_id
        if chapter_id not in chapters:
            chapters.append(chapter_id)
            
    chapters_performance=[]
    
    for chapter in chapters:
        student_answers = StudentAnswers.objects.filter(student_id__exact = student_id, 
                                                        question__chapter__exact = chapter,
                                                    question__test__exact = test_id)
        temp_dict = {}
        temp_dict[student_answers[0].question.chapter.name] =  {"total_marks":0,"marks_scored":0}
        for answer in student_answers:
            
            temp_dict[answer.question.chapter.name]["total_marks"] = temp_dict[answer.question.chapter.name]["total_marks"] + int(answer.question.correct_score)
            temp_dict[answer.question.chapter.name]["marks_scored"] = temp_dict[answer.question.chapter.name]["marks_scored"] + answer.score
            
        chapters_performance.append(temp_dict)
        
        
    """student_answers = StudentAnswers.objects.filter(student_id__exact = student_id, 
                                                    question__test__exact = test_id)
    chapters_performance=[]
    
    for answer in student_answers:
        temp_dict={}
        
        temp_dict[answer.question.chapter.name] = {"total_marks":0,"marks_scored":0}
        temp_dict[answer.question.chapter.name]["total_marks"] = temp_dict[answer.question.chapter.name]["total_marks"] + int(answer.question.correct_score)
        temp_dict[answer.question.chapter.name]["marks_scored"] = temp_dict[answer.question.chapter.name]["marks_scored"] + answer.score
        
        chapters_performance.append(temp_dict)"""
    
    return chapters_performance

#cohort methods
"""def get_cohort(metric, filter_type, filter_detail, subject="0", startdate, enddate):
    if metric == "1": #instirank
        if subject!="0": #there needn't be a filter as well
            if filter_type == "1": #chapter
                chapter = filter_detail
                
        return 0"""

def get_cohort(request):
    if request.is_ajax() or request.method == "GET":
        current_user = request.user
        current_user_id = current_user.id
        
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        
        tests = models_tests.TestPerformance.objects.filter(student_id__exact = current_user_id,
                                                            test__test_date__range=[start_date, end_date])
        results = []
        for test in tests:
            test_json = {}
            test_json["names"] = test.test.name
            test_json["insti_rank"] = test.insti_rank
            test_json["overall_score"] = test.overall_score
            test_json["date"] = json.dumps(test.test.test_date.isoformat())
            
            results.append(test_json)
            
        
        data = simplejson.dumps(results)
        print data
    else:
        data = 'fail'
        mimetype = 'application/json'
    return HttpResponse(data, 'application/json')



def logout_action(request):
    logout(request)
    return HttpResponseRedirect('/students')
    