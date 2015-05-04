from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.db.models import Q
from allaccess.views import OAuthCallback
from allaccess.models import AccountAccess
from s_network.models import *

# Create your views here.

DEFAULT_PIC = 's_network/images/user_blank.jpg'


def home(request):
    """ displays the home page of the app, allows a user to log in manually,
    with facebook or register as a new user """

    if request.user.username:
        try:
            p = Profile.objects.get(user=request.user)
        except:
            bad_username = request.user

            context = {
                'bad_username': bad_username,
            }

            return render(request, 's_network/extended_failed_facebook_login.html', context)

        url = '/s_network/'+request.user.username
        return HttpResponseRedirect(url)
    else:
        return render(request, 's_network/extended_home.html')


def register(request):
    """ creates new user and profile entries for a user and redirects to the
    newly created profile. Checks that required fields are present and that
    the password and password_confirm are the same """

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        first_name = request.POST.get('first_name')
        birthday = request.POST.get('birthday')

        if not (username and password and password_confirm and email):
            return render(request, 's_network/extended_register_failed.html')

        if not password == password_confirm:
            return render(request, 's_network/extended_register_failed.html')

        user = User.objects.create_user(username, email, password,
                                        first_name=first_name,
                                        last_name=last_name)

        user = authenticate(username=username, password=password)

        new_profile = Profile(user=user, first_name=first_name,
                            last_name=last_name, birthday=birthday,
                            email=email)
        new_profile.save()

        login(request, user)
        url = '/s_network/'+user.username
        return HttpResponseRedirect(url)

    return render(request, 's_network/extended_register.html')


def user_login(request):
    """ logs in user """

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)
        url = '/s_network/'+user.username
        return HttpResponseRedirect(url)

    return render(request, 's_network/extended_login.html')


def logout(request):
    """ logs out the currently logged in user """

    auth.logout(request)

    return HttpResponseRedirect(reverse('home'))


def failed_fb_login(request):
    """ when allaccess attempts a facebook login and there is
    no access_account for the current user it creates a dummy
    user with that facebook id's info, this function serves to
    set the newly created access_account's user to the correct
    person by having that person use their login credentials
    to verify they are the person whose facebook was just used
    to login. it then deletes the dummy user and redirects to
    the user's profile. """

    if request.method == 'POST':
        correct_username = request.POST.get('username')
        password = request.POST.get('password')
        bad_username = request.POST.get('bad_username')

        if authenticate(username=correct_username, password=password):
            bad_user = User.objects.get(username=bad_username)

            access_account = AccountAccess.objects.get(user=bad_user)
            access_account.user = User.objects.get(username=correct_username)
            access_account.save()

            delete_user = User.objects.get(username=bad_username)
            delete_user.delete()

            url = '/s_network/'+correct_username
            return HttpResponseRedirect(url)
        else:
            return HttpResponse('<h1>Your login has failed</h1>')


def new_wall_post(request):
    """ creates a new wall post object attached to the profile currently being viewed
    and refreshes that user's page to display it """

    if request.method == 'POST':
        text = request.POST.get('text')
        profile_user = request.POST.get('profile_user')
        poster = Profile.objects.get(user__username=(request.POST.get('poster')))
        user = Profile.objects.get(user__username=profile_user)
        if text:
            new_post = WallPost(profile=user, poster=poster,
                                post_text=text, post_date_time=timezone.now())
            new_post.save()

    return redirect('/s_network/'+profile_user)


def delete_wall_post(request):
    """ Deletes a wallpost """

    if request.method == 'POST':
        post_id = request.POST.get('id')
        profile_user = request.POST.get('profile_user')
        post = WallPost.objects.get(id=post_id)
        post.delete()

        return redirect('/s_network/'+profile_user)


def new_comment(request):
    """ creates a new comment object attatched to a specific wall post """

    if request.method == 'POST':
        text = request.POST.get('text')
        post_id = request.POST.get('id')
        post = WallPost.objects.get(id=post_id)
        commenter = Profile.objects.get(user__username=(request.POST.get('commenter')))
        if text:
            new_comment = Comment(wallpost=post, commenter=commenter,
                                comment_text=text, comment_date_time=timezone.now())
            new_comment.save()

    return redirect('/s_network/'+post.profile.user.username)


def delete_comment(request):
    """ Deletes a comment """

    if request.method == 'POST':
        comment_id = request.POST.get('id')
        profile_user = request.POST.get('profile_user')
        comment = Comment.objects.get(id=comment_id)
        comment.delete()

        return redirect('/s_network/'+profile_user)


def see_all_posts(request, username):
    """ Allows the a user to view all of the wallposts on a profile
    vs only the latest 3 in the regular profile view """

    user = Profile.objects.get(user__username=username)
    logged_in_user_object = request.user
    
    post_list = WallPost.objects.filter(profile=user)
    passed_username = logged_in_user_object.username

    wall_posts = []
    comments = []

    if user.profile_pic:
        profile_picture = photo_url_fix(user.profile_pic.url)
    else:
        profile_picture = DEFAULT_PIC

    for post in post_list:
        comment_list = post.comment_set.all()
        for comment in comment_list:
            comments.append(comment)
        wall_posts.append(post)

    context = {
        'user': passed_username,
        'profile_pic': profile_picture,
        'wall_posts': wall_posts,
        'comments': comments,
        'first_name': user.first_name,
        'username': user.user.username,
    }

    return render(request, 's_network/extended_all_posts.html', context)


def profile(request, username):
    """ gathers information to send to extended_userprofile.html and renders it. """
    
    user = Profile.objects.get(user__username=username)
    logged_in_user_object = request.user

    passed_username = logged_in_user_object.username
    if not request.user.is_authenticated():
        return redirect('/s_network/login/?next=%s' % request.path)
    else:
        post_list = WallPost.objects.filter(profile=user)

        r_name = user.first_name+' '+user.last_name
        first_name = user.first_name
        if user.profile_pic:
            profile_picture = photo_url_fix(user.profile_pic.url)
        else:
            profile_picture = DEFAULT_PIC

        wall_posts = []
        comments = []
        for post in post_list:
            comment_list = post.comment_set.all()
            for comment in comment_list:
                comments.append(comment)
            wall_posts.append(post)
        wall_posts = wall_posts[-3:]

        context = {
            'user': passed_username,
            'username': username,
            'r_name': r_name,
            'first_name': first_name,
            'profile_pic': profile_picture,
            'wall_posts': reversed(wall_posts),
            'comments': comments,
        }

        return render(request, 's_network/extended_userprofile.html', context)


def info(request, username):
    """ gathers the info and sends it to extended_info.html to display """
    if not request.user.is_authenticated():
        return redirect('/s_network/login/?next=%s' % request.path)

    profile = Profile.objects.get(user__username=username)

    r_name = profile.first_name
    b_day = profile.birthday
    email = profile.email

    context = {
        'r_name': r_name,
        'b_day': b_day,
        'email': email,
        'username': username
    }

    return render(request, 's_network/extended_info.html', context)


def choose_profile_pic(request, username):
    """ enables the user to choose a new profile picture to display """

    user = Profile.objects.get(user__username=username)
    pic_list = user.photo_set.all()
    new_list = []
    for pic in pic_list:
        new_list.append(photo_url_fix(pic.photo.url))

    logged_in_user_object = request.user

    passed_username = logged_in_user_object.username

    context = {
        'pic_list': new_list,
        'user': passed_username,
        'username': user.user.username,
    }

    return render(request, 's_network/extended_choose_profile_pic.html', context)


def update_profile_pic(request):
    """ Updates a user's profile pic field in the profile model,
    helps choose_profile_pic() """

    if request.method == 'POST':
        pic_url = request.POST.get('pic_url')

    username = request.user.username
    user = Profile.objects.get(user__username=username)
    new_profile_pic_list = user.photo_set.all()

    for pic in new_profile_pic_list:
        if(pic.photo.url.endswith(pic_url)):
            new_profile_pic = pic

    user.profile_pic = new_profile_pic.photo.url
    user.save()

    url = '/s_network/'+username
    return HttpResponseRedirect(url)


def edit_profile(request, username):
    """ enables the user to edit some of their profile information """

    user = Profile.objects.get(user__username=username)
    logged_in_user_object = request.user
    passed_username = logged_in_user_object.username

    context = {
        'user': passed_username,
        'username': user.user.username,
    }

    return render(request, 's_network/extended_edit_profile.html', context)


def update_profile(request):
    """ updates the information supplied by the user via extended_edit_profile.html """

    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        user = Profile.objects.get(user__username=request.user.username)

        if email:
            user.email = email
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name

        user.save()

        url = '/s_network/'+user.user.username
        return HttpResponseRedirect(url)


def upload_pics(request, username):
    """ enables the user to upload photos to their profile, it also displays the
    user's other photos """

    user = Profile.objects.get(user__username=username)
    pic_list = user.photo_set.all()
    new_list = []
    for pic in pic_list:
        new_list.append(photo_url_fix(pic.photo.url))

    logged_in_user_object = request.user
    passed_username = logged_in_user_object.username

    context = {
        'pic_list': new_list,
        'user': passed_username,
        'username': user.user.username,
    }

    return render(request, 's_network/extended_upload_pics.html', context)


def insert_photo(request):
    """ helps upload_pics() insert photos into the DB """

    if request.method == 'POST':
        pic = request.FILES['the_file']

        user = Profile.objects.get(user__username=request.user.username)

        new_pic = Photo(profile=user, photo=pic)
        new_pic.save()

        url = '/s_network/'+user.user.username+'/photos'
        return HttpResponseRedirect(url)


def photo_album(request, username):
    """ creats a list of the user whose profile is currently displayed
    photos to send to photos.html to render """

    if not request.user.is_authenticated():
        return redirect('/s_network/login/?next=%s' % request.path)

    user = Profile.objects.get(user__username=username)
    pic_list = user.photo_set.all()
    new_list = []
    for pic in pic_list:
        new_list.append(photo_url_fix(pic.photo.url))

    context = {
        'username': username,
        'first_name': user.first_name,
        'pic_list': new_list,
    }
    return render(request, 's_network/photos.html', context)


def user_search(request):
    """ renders extended_user_search.html to gather info to search for users """

    if not request.user.is_authenticated():
        return redirect('/s_network/login/?next=%s' % request.path)

    context = {
        'username': request.user.username,
        }
    return render(request, 's_network/extended_user_search.html', context)


def search_results(request):
    """ gathers the information provided on extended_user_search, performs the query
    and displays the results. """

    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')

    qs = User.objects.all()

    qs = qs.filter(Q(first_name__icontains=first_name) & Q(last_name__icontains=last_name)
                    & Q(email__icontains=email) & Q(username__icontains=username))
    context = {
        'results': qs,
    }

    return render(request, 's_network/extended_search_results.html', context)


def photo_url_fix(url):
    """ fixes the regular ImageField url to work for loading static files """

    return url[17:]
