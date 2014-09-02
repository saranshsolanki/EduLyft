from ajax_select.fields import AutoCompleteField
import bisect
from django import forms
from django.contrib.auth.models import User
from django.core import serializers
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext, loader
from django.utils import simplejson
import xlrd

from Students.forms import TestAndStudentNameForm, StudentAnswersForm
from Students.models import StudentAnswers
from models import ChaptersList
from models import QuestionsForm, TestsForm, Questions, Tests
from models import SubjectsList, TestPerformance
from models import XlsInputForm


# Create your views here.
def index(request):
    if request.method == 'GET':
        form = TestsForm()
        return render_to_response('tests/index.html', {'TestsForm': form}, 
                              context_instance=RequestContext(request))

    elif request.method == 'POST':
        form = TestsForm(request.POST)
        if form.is_valid():
            saved_test = form.save()
            saved_test_id = saved_test.pk
            saved_test_name = saved_test.name
            saved_no_questions = saved_test.no_of_questions
            request.session['saved_test_id'] = saved_test_id
            request.session['saved_test_name'] = saved_test_name
            request.session['saved_no_questions'] = saved_no_questions
            
            return HttpResponseRedirect("/tests/create")
        else:
            return render_to_response('tests/index.html', {'TestsForm': form}, 
                              context_instance=RequestContext(request))
    
def create(request):
    saved_test_id = request.session.get('saved_test_id')
    saved_test_name = request.session.get('saved_test_name')
    saved_no_questions = request.session.get('saved_no_questions')
    
    test_instance = Tests.objects.get(id=saved_test_id)
    QuestionFormSet = modelformset_factory(Questions,form = QuestionsForm, extra=int(saved_no_questions))
            
    if request.method == 'GET':
        qs = Questions.objects.none()
        formset = QuestionFormSet(queryset=qs, initial=[{'question_no': x + 1} for x in xrange(int(saved_no_questions))])
        return render_to_response('tests/questions.html', 
                                      {'formset':formset, 'saved_test_id': saved_test_id,
                                       'saved_test_name': saved_test_name}, 
                                      context_instance=RequestContext(request))
    if request.method == 'POST':
        formset = QuestionFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                questions = Questions()
                questions.test = test_instance
                questions.question_no = form.cleaned_data['question_no']
                questions.subject = form.cleaned_data['subject']
                questions.chapter = form.cleaned_data['chapter']
                questions.answer = form.cleaned_data['answer']
                questions.lod = form.cleaned_data['lod']
                questions.type = form.cleaned_data['type']
                questions.correct_score = form.cleaned_data['correct_score']
                questions.wrong_score = form.cleaned_data['wrong_score']
                questions.save()
            
                
            return HttpResponse("Test has been created.")
        else:
            return render_to_response('tests/questions.html', 
                                      {'formset':formset, 'saved_test_id': saved_test_id,
                                       'saved_test_name': saved_test_name}, 
                                      context_instance=RequestContext(request))

def upload_student_marks(request):
    if request.method == 'GET':
        form = TestAndStudentNameForm()
        #excelform = XlsInputForm()
        
    elif request.method == 'POST':
        form = TestAndStudentNameForm(request.POST,request.FILES)
        #excelform = XlsInputForm(request.POST, request.FILES)
        
        if form.is_valid():
            testname = request.POST.get('testname','')
            studentname = request.POST.get('studentname','')
            input_excel = request.FILES['input_excel']
            
            student_response_list = get_student_response_from_excel_file(input_excel)
            request.session['testname'] = testname
            request.session['studentname'] = studentname
            request.session['student_response_list'] = student_response_list
            
            return HttpResponseRedirect("/tests/upload_marks_final")
        else:
            return HttpResponse("Error")
    return render_to_response('tests/upload_student_marks.html', {'form': form},
                             context_instance=RequestContext(request))
            
def upload_marks_final(request):
    studentname = request.session.get('studentname')
    student = User.objects.get(username__exact = studentname)
    student_id = student.id
    
    testname = request.session.get('testname')
    test = Tests.objects.get(name__exact = testname)
    test_id = test.id
    
    student_response_list = request.session.get('student_response_list')
    
    questions_len = Questions.objects.filter(test_id__exact = test_id).count()
    student_response_list = student_response_list[:int(questions_len)]
    StudentAnswersFormSet = formset_factory(StudentAnswersForm, max_num=int(questions_len))
        
    if request.method == 'GET':
        qs = StudentAnswers.objects.none()
        #formset = StudentAnswersFormSet(initial=[{'question': x + 1} for x in xrange(int(questions_len))])
        formset = StudentAnswersFormSet(initial=[{'question_no': int(x[0]),'attempt_ans':x[1]} for x in student_response_list])
        return render_to_response('tests/upload_marks_final.html', {'formset':formset},
                             context_instance=RequestContext(request))
    
    elif request.method == 'POST':
        formset = StudentAnswersFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                question_no = form.cleaned_data['question_no']
                attempt_ans = form.cleaned_data['attempt_ans']
                
                question = get_question(test_id,question_no)
                score_details = get_score(question, attempt_ans)
                
                score = score_details[0]
                    
                student_answer = StudentAnswers()
                student_answer.student = student
                student_answer.attempt_ans = attempt_ans
                student_answer.question = question
                student_answer.score = score
                student_answer.is_answered = score_details[1]
                student_answer.is_correct = score_details[2]
                student_answer.save()
                
            physics_score = get_subject_marks(student_id,test_id,1)
            chemistry_score = get_subject_marks(student_id,test_id,2)
            math_score = get_subject_marks(student_id,test_id,3)
    
            overall_score = physics_score + chemistry_score + math_score    
            
            overall_ordered_students = get_ordered_students_for_test(test_id,'-overall_score')
            physics_ordered_students = get_ordered_students_for_test(test_id,'-physics_score')
            chem_ordered_students = get_ordered_students_for_test(test_id,'-chemistry_score')
            math_ordered_students = get_ordered_students_for_test(test_id,'-math_score')
            
            
            if not overall_ordered_students:
                insti_rank = 1
                
            else:
                insti_rank = get_overall_rank(overall_ordered_students,overall_score, student_id)
                
            if not physics_ordered_students:
                phy_insti_rank = 1
            else:
                phy_insti_rank = get_phy_rank(physics_ordered_students,physics_score, student_id)
            
            if not chem_ordered_students:
                chem_insti_rank = 1
            else:
                chem_insti_rank = get_chem_rank(chem_ordered_students,chemistry_score, student_id)
                
            if not math_ordered_students:
                math_insti_rank = 1
            else:
                math_insti_rank = get_math_rank(math_ordered_students,math_score, student_id)
            
            store_test_performance(student, test, physics_score, chemistry_score, math_score, 
                                   overall_score, insti_rank, phy_insti_rank,chem_insti_rank,
                                   math_insti_rank)
            
            if overall_ordered_students:
                update_overall_insti_ranks(insti_rank,overall_ordered_students)
            if physics_ordered_students:
                update_phy_insti_ranks(phy_insti_rank, physics_ordered_students)
            if chem_ordered_students:
                update_chem_insti_ranks(chem_insti_rank, chem_ordered_students)
            if math_ordered_students:
                update_math_insti_ranks(math_insti_rank, math_ordered_students)
            
            return HttpResponse("Marks have been uploaded.")
        else:
            return render_to_response('tests/upload_marks_final.html', {'formset':formset},
                             context_instance=RequestContext(request))

def get_student_response_from_excel_file(input_excel):
    book = xlrd.open_workbook(file_contents=input_excel.read())
    worksheet = book.sheet_by_index(0)
    num_rows = worksheet.nrows - 1
    num_cells = worksheet.ncols - 1
    curr_row = -1
    
    values = []
    while curr_row < num_rows:
        curr_row += 1
        row = worksheet.row(curr_row)
        curr_cell = -1
        row_value = []
        while curr_cell < num_cells:
            curr_cell += 1
            # Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
            cell_type = worksheet.cell_type(curr_row, curr_cell)
            cell_value = worksheet.cell_value(curr_row, curr_cell)
            row_value.append(cell_value)
        values.append(row_value)
    
    return values



def get_subject_marks(current_user, test_id, subject_id):
    answers = StudentAnswers.objects.filter(student_id__exact = current_user, 
                                  question__test__exact = test_id, 
                                  question__subject__exact = subject_id)
    overall_score = 0
    for answer in answers:
        score = int(answer.score)
        overall_score = overall_score + score
    return overall_score

def get_ordered_students_for_test(test_id, param):
    students = TestPerformance.objects.filter(test_id__exact = test_id).order_by(param)
    print "students:", students       
    return students

def get_overall_rank(ordered_students, overall_score, student_id):
    new_student_score = overall_score
    overall_scores = []
    for student in ordered_students:
        overall_scores.append(student.overall_score)
    reverse_overall_scores = overall_scores[::-1]
    
    i = bisect.bisect_left(reverse_overall_scores, new_student_score)
    rank = len(reverse_overall_scores) - i + 1
    
    return rank

def get_phy_rank(ordered_students, overall_score, student_id):
    new_student_score = overall_score
    overall_scores = []
    for student in ordered_students:
        overall_scores.append(student.physics_score)
    reverse_overall_scores = overall_scores[::-1]
    
    i = bisect.bisect_left(reverse_overall_scores, new_student_score)
    rank = len(reverse_overall_scores) - i + 1
    
    return rank

def get_chem_rank(ordered_students, overall_score, student_id):
    new_student_score = overall_score
    overall_scores = []
    for student in ordered_students:
        overall_scores.append(student.chemistry_score)
    reverse_overall_scores = overall_scores[::-1]
    
    i = bisect.bisect_left(reverse_overall_scores, new_student_score)
    rank = len(reverse_overall_scores) - i + 1
    
    return rank

def get_math_rank(ordered_students, overall_score, student_id):
    new_student_score = overall_score
    overall_scores = []
    for student in ordered_students:
        overall_scores.append(student.math_score)
    reverse_overall_scores = overall_scores[::-1]
    i = bisect.bisect_left(reverse_overall_scores, new_student_score)
    rank = len(reverse_overall_scores) - i + 1
    
    return rank

def store_test_performance(student, test, physics_score, chemistry_score, math_score, overall_score, 
                           insti_rank, phy_insti_rank, chem_insti_rank, math_insti_rank):
    test_performance = TestPerformance()
    test_performance.student = student
    test_performance.test = test
    test_performance.physics_score = physics_score
    test_performance.chemistry_score = chemistry_score
    test_performance.math_score = math_score
    test_performance.overall_score = overall_score
    test_performance.insti_rank = insti_rank
    test_performance.phy_insti_rank = phy_insti_rank
    test_performance.chem_insti_rank = chem_insti_rank
    test_performance.math_insti_rank = math_insti_rank
    
    test_performance.save()
    
def update_overall_insti_ranks(insti_rank,ordered_students):
    for i in range(insti_rank - 1, len(ordered_students)):
        student = ordered_students[i]
        student_id = student.student_id
        #print student_id
        test_performance = TestPerformance.objects.get(student_id__exact = student_id)
        #print test_performance.insti_rank
        test_performance.insti_rank = test_performance.insti_rank + 1
        test_performance.save()

def update_phy_insti_ranks(phy_insti_rank,ordered_students):
    for i in range(phy_insti_rank - 1, len(ordered_students)):
        student = ordered_students[i]
        student_id = student.student_id
        #print student_id
        test_performance = TestPerformance.objects.get(student_id__exact = student_id)
        #print test_performance.insti_rank
        test_performance.phy_insti_rank = test_performance.phy_insti_rank + 1
        test_performance.save()
        
def update_chem_insti_ranks(chem_insti_rank,ordered_students):
    for i in range(chem_insti_rank - 1, len(ordered_students)):
        student = ordered_students[i]
        student_id = student.student_id
        #print student_id
        test_performance = TestPerformance.objects.get(student_id__exact = student_id)
        #print test_performance.insti_rank
        test_performance.chem_insti_rank = test_performance.chem_insti_rank + 1
        test_performance.save()
        
def update_math_insti_ranks(math_insti_rank,ordered_students):
    for i in range(math_insti_rank - 1, len(ordered_students)):
        student = ordered_students[i]
        student_id = student.student_id
        #print student_id
        test_performance = TestPerformance.objects.get(student_id__exact = student_id)
        #print test_performance.insti_rank
        test_performance.math_insti_rank = test_performance.math_insti_rank + 1
        test_performance.save()

def get_question(test_id, question_no):
    question = Questions.objects.get(test_id__exact = test_id, question_no__exact = question_no)
    return question

def get_score(question, attempt_ans):
    is_correct = None
    if attempt_ans == '':
        score = 0
        is_answered = False
    elif attempt_ans == question.answer:
        score = question.correct_score
        is_answered = True
        is_correct = True
    else:
        score = question.wrong_score
        is_answered = True
        is_correct = False
        
    score_details = [score,is_answered,is_correct]    
    return score_details


def get_all_tests(request):
    if request.is_ajax() or request.method == "GET":
        q = request.GET.get('term', '')
        tests = Tests.objects.filter(name__icontains = q)[:10]
        #print tests
        results = []
        for test in tests:
            test_json = {}
            test_json['name'] = test.name
            results.append(test_json['name'])
        data = simplejson.dumps(results)
        #print data
    else:
        data = 'fail'
        mimetype = 'application/json'
    return HttpResponse(data, 'application/json')

def get_students(request):
    if request.is_ajax() or request.method == "GET":
        q = request.GET.get('term', '')
        students = User.objects.filter(username__icontains = q)[:10]
        #print tests
        results = []
        for student in students:
            student_json = {}
            student_json['username'] = student.username
            results.append(student_json['username'])
        data = simplejson.dumps(results)
        #print data
    else:
        data = 'fail'
        mimetype = 'application/json'
    return HttpResponse(data, 'application/json')

def get_subjects(request):
    if request.is_ajax() or request.method == "GET":
        q = request.GET.get('term', '')
        subjects = SubjectsList.objects.filter(name__icontains = q)[:10]
        #print tests
        results = []
        for subject in subjects:
            subject_json = {}
            subject_json['name'] = subject.name
            results.append(subject_json['name'])
        data = simplejson.dumps(results)
        #print data
    else:
        data = 'fail'
        mimetype = 'application/json'
    return HttpResponse(data, 'application/json')

def get_chapters(request):
    if request.is_ajax() or request.method == "GET":
        q = request.GET.get('term', '')
        subject_entry = request.GET.get('subject', '')
        subject = SubjectsList.objects.get(name__exact = subject_entry)
        chapters = ChaptersList.objects.filter(subject__exact = subject.id,
                                               name__icontains = q)[:10]
        #print chapters
        #print tests
        results = []
        for chapter in chapters:
            chapter_json = {}
            chapter_json['name'] = chapter.name
            results.append(chapter_json['name'])
        data = simplejson.dumps(results)
        print data
    else:
        data = 'fail'
        mimetype = 'application/json'
    return HttpResponse(data, 'application/json')

 