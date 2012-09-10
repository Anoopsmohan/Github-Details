import simplejson
from urllib2 import *

from django.template import loader, Context
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def index(request):
    """
    Render the index page
    """
    return render_to_response('index.html')


def user_resume(request):
    """
    Generate the resume for the corresponding username.
    """
    user_name = request.POST.get('resume')
    user_name = '-'.join(user_name.split(' '))
    try:
        user = urlopen('https://api.github.com/users/'+user_name)
        result_user = simplejson.load(user)
        created_at = result_user['created_at'].split('-')
        created_at = created_at[0]
        result_org = None
        list_repo = None
        langs = {}
        org = {}
        newlist = []
        try:
            if result_user['type'] == 'Organization':
                org['type'] = result_user['login']
            else:
                org['type'] = None
            repo = urlopen('https://api.github.com/users/'+user_name+'/repos')
            result_repo = simplejson.load(repo)
            list_repo = result_repo[::-1]
            for dicts in list_repo:
                repo_create = dicts['created_at'].split('-')
                repo_create = repo_create[0]
                for x,y in dicts.items():
                    dicts['created_at'] = repo_create
                fork = dicts['fork']
                lang = dicts['language']
                if lang in langs and fork != True:
                    langs[lang] += 1
                elif lang != '' and lang != 'null' and lang != None\
                        and fork != True:
                    langs[lang] = 1
                total = langs.values()
                total = reduce(lambda x, y:x+y, total)
                for x,y in langs.items():
                    langs[x] = int((float(y)/float(total))*100)
                filter_repo_list = []
                for dicts in list_repo:
                    watchers = dicts['watchers']
                    forks = dicts['forks']
                    priority = watchers + forks
                    dicts['priority'] = priority
                    if dicts['fork'] != True:
                        filter_repo_list.append(dicts)
                    newlist = (
                        (
                            sorted(
                                filter_repo_list, key=lambda k: k['priority']
                            )
                        )[::-1]
                    )[:5]
                    message=''
        except:
            message = "Username doesnot exist. Try with another username."
        t = loader.get_template('resume.html')
        c = Context(
            {
                'created_at': created_at,
                'lists': result_user,
                'repos': newlist,
                'orgs': result_org,
                'langs': langs,
                'message': message
            }
        )
        return HttpResponse(t.render(c))
    except URLError, e:
        msg='''The username you submitted (%s) doesnot appear to be a valid\
        one! <br/>%s.''' %(request.POST.get('resume'),str(e))
        return handleError(request,msg,'index.html')


def email_send(request):
    """
    Users can send email to administrator from contacts
    """
    email = ''
    name = ''
    msg = ''
    email = str(request.POST.get('email'))
    name = str(request.POST.get('name'))
    message = str(request.POST.get('msg'))
    warning = ''
    success = ''
    success1 = ''
    error = ''
    body = "Email from : "+name+"\nEmail : "+email+"\n\nMessage : \n\n"+message
    if email and name and message:
	try:
            try:
                validate_email( email )
                subject, from_email, to, bcc = "Reply from Github Details",\
                    "anoopmhn2009@gmail.com", email, "anoop@beevolve.com"
                html_content = render_to_string('email.html', {'name': name})
                textcontent = render_to_string('email.txt',  {'name':name})
                text_content = strip_tags(textcontent)
                msg = EmailMultiAlternatives(
                    subject, text_content, from_email, [to],[bcc]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                success = "Your Email id verified successfully.\
                    Please check your Inbox"
                try:
                    email_msg = EmailMessage (
                        'Email from Github Accound Details',
                        body,
                        to=['anoopmhn2009@gmail.com']
                    )
                    email_msg.send()
                    success1 = "Email send Successfully!"
                except:
                    error = "There was a problem. Please try after some time"
            except ValidationError:
                error = "Invalid Email Id, please correct it!"
        except:
            error = "There was a problem while sending the email.\
                Please check your email Id"
    else:
        if not email:
            warning = "Please enter the email!"
        elif not name:
            warning = "Please enter the name!"
        elif not message:
            warning = "Please enter the message!"
        c = RequestContext(
            request,{
                'warning': warning,
                'success': success,
                'success1': success1,
                'error': error,
                'name': name,
                'msg': message,
                'email': email
            }
        )
    return render_to_response('contact.html',c)


def contact(request):
    """
    Render the contact page.
    """
    return render_to_response('contact.html')


def handleError(request,msg,template,param=None):
    if param is None:
	param={}
    param['error']=msg
    return render_to_response(template,param)


def username_search(request):
    user_name = request.POST.get('user_search')
    user_name = '-'.join(user_name.split(' '))
    try:
        user = urlopen('https://api.github.com/users/'+user_name)
        result_user = simplejson.load(user)
        org={}
        list_repo=None
        try:
            if result_user['type'] == 'Organization':
                org['type'] = result_user['login']
            else:
                org['type'] = None
            repo = urlopen(
                'https://api.github.com/users/'+ user_name +'/repos'
            )
            result_repo = simplejson.load(repo)
            list_repo = result_repo[::-1]
            message=''
        except:
            message = "Username doesnot exist. Try with another username."
        t = loader.get_template('details.html')
        c =Context(
            {
                'name': user_name,
                'lists': result_user,
                'repos': list_repo,
                'org_type': org,
                'message': message
            }
        )
        return HttpResponse(t.render(c))
    except URLError, e:
        msg='''The username you submitted (%s) doesnot appear to be a\
            valid one! <br/>%s.''' %(request.POST.get('user_search'),str(e))
        return handleError(request,msg,'index.html')


def topic_search(request):
    topic = request.POST.get('searchbox')
    topic = '-'.join(topic.split(' '))
    try:
        topic_details = urlopen(
            'https://api.github.com/legacy/repos/search/'+topic
        )
        result = simplejson.load(topic_details)
        data= result['repositories']
        num_result = len(data)
        if len(data)!= 0:
            message = " "
        else:
            message = "No data found. Please search another keyword."
        c=Context(
            {
                'data_list': data,
                'message': message,
                'topic': topic,
                'num_result': num_result
            }
        )
        return render_to_response('topic_details.html',c)
    except URLError, e:
        msg='''The topic you submitted (%s) doesnot appear to be a valid one!\
        <br/>%s.''' %(request.POST.get('user_search'),str(e))
        return handleError(request,msg,'index.html')


def details(request, user_name, topic_name=None):
    user = urlopen('https://api.github.com/users/'+user_name)
    result_user = simplejson.load(user)
    org={}
    if result_user['type'] == 'Organization':
        org['type'] = result_user['login']
    else:
        org['type'] = None
    repo = urlopen('https://api.github.com/users/'+ user_name +'/repos')
    result_repo = simplejson.load(repo)
    list_repo = result_repo[::-1]
    t = loader.get_template('details.html')
    c =Context(
        {
            'name': user_name,
            'lists': result_user,
            'repos': list_repo,
            'org_type': org
        }
    )
    return HttpResponse(t.render(c))


def org_details(request, org_name, user_name=None):
    org = urlopen('https://api.github.com/orgs/'+org_name+'/members')
    org_members = simplejson.load(org)
    num_emp = len(org_members)
    list_repo = None
    result_user = None
    if user_name:
        user = urlopen('https://api.github.com/users/'+user_name)
        result_user = simplejson.load(user)
        repo = urlopen('https://api.github.com/users/'+user_name+'/repos')
        result_repo = simplejson.load(repo)
        list_repo = result_repo[::-1]

    t = loader.get_template('org_details.html')
    c = Context(
        {
            'name_list': org_members,
            'org_name': org_name,
            'num_emp': num_emp,
            'repos': list_repo,
            'lists': result_user
        }
    )
    return HttpResponse(t.render(c))
