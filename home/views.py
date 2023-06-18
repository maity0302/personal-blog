from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from django.db.models import Q
from django.db.models import Count
from django.contrib import messages
from django.utils import timezone
from .models import Blog, Reaction, User, Collection, Comment
from datetime import datetime, timedelta, date
import readtime
from .validates import *
from django.db.models import F

# Create your views here.


def index(request):
    try:
        blogs = Blog.objects.filter(status=True).order_by('-createdat')[:3]
        # Get 6 blog have most like
        today = date.today()
        past = today - timedelta(days=30)
        # query top blogs created in 30 days and status is true
        topblogs = Blog.objects.filter(createdat__range=(past, today), status=True).annotate(
            like_count=Count('reaction', filter=Q(reaction__reaction='like')),
        ).order_by('-like_count')[:6]

        # query top user create blog with count Blog
        topusers = User.objects.annotate(
            blog_count=Count('blogs')).order_by('-blog_count')[:3]
        # query random 10 collection to show in home page
        collections = Collection.objects.filter().order_by('?')[:10]
    except Blog.DoesNotExist:
        raise Http404("Dữ liệu không tồn tại")
    return render(request, 'pages/home.html',
                  {'blogs': blogs, 'topblogs': topblogs, 'topusers': topusers, 'collections': collections, })


def blogs(request):
    try:
        latestblogs = Blog.objects.filter(status=True).order_by('-createdat')
    except Blog.DoesNotExist:
        raise Http404("Dữ liệu không tồn tại")
    return render(request, 'pages/blogs.html', {'blogs': latestblogs, })


def chitiet(request, id):
    try:
        blog = Blog.objects.get(id=id)
        lastViewed = request.session.get(f'lastViewed{id}')
        if lastViewed:
            lastViewed = timezone.make_aware(
                datetime.strptime(lastViewed, "%Y-%m-%d %H:%M:%S"))
        # Check if the blog has been viewed in the last 24 hours
        if lastViewed is None or (timezone.now() - lastViewed) >= timezone.timedelta(days=1):
            blog.view += 1
            blog.save()
            # Save the current timestamp in the session
            request.session[f'lastViewed{id}'] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S")
        # Get read time of blog
        blogreadtime = f"{readtime.of_html(blog.content).minutes}"

        # Get 9 random blog
        randomblogs = Blog.objects.filter(status=True).order_by('?')[:9]
        # Set default value for like and dislike
        reaction = None
        # Send reaction of user if user has logged in to check like or dislike
        if request.session.get('user'):
            user = User.objects.get(email=request.session['user']['email'])
            try:
                userReaction = Reaction.objects.get(iduser=user, idblog=blog)
                reaction = userReaction.reaction
            except Reaction.DoesNotExist:
                reaction = None
        # Get the number of likes and dislikes for the blog
        counts = Reaction.objects.filter(idblog=blog).aggregate(
            like_count=Count('reaction', filter=Q(reaction='like')),
            dislike_count=Count('reaction', filter=Q(reaction='dislike'))
        )
        like_count = counts['like_count']
        dislike_count = counts['dislike_count']
        # Get all comments of blog
        comments = Comment.objects.filter(idblog=blog).order_by('-createdat')
    except Blog.DoesNotExist:
        raise Http404("Blog không tồn tại")
    return render(request, 'pages/chitiet.html', {'blog': blog, 'randomblogs': randomblogs,
                                                  'like_count': like_count, 'dislike_count': dislike_count,
                                                  'reaction': reaction,
                                                  'comments': comments,
                                                  'blogreadtime': blogreadtime,
                                                  })


def reaction(request, blogId):
    if request.session.get('user'):
        user = User.objects.get(email=request.session['user']['email'])
        blog = Blog.objects.get(id=blogId)
        reaction = request.POST.get('reaction')
        # Check reaction is like or dislike
        if reaction not in ['like', 'dislike']:
            return redirect('/blog/' + str(blogId))
        try:
            # Check if user has reacted to the blog
            userReaction = Reaction.objects.get(iduser=user, idblog=blog)
            if userReaction.reaction == reaction:
                # If the user has reacted to the blog, delete the reaction
                userReaction.delete()
            else:
                # If the user has reacted to the blog, update the reaction
                userReaction.reaction = reaction
                userReaction.save()
        except Reaction.DoesNotExist:
            # Create new reaction
            newReaction = Reaction(
                iduser=user, idblog=blog, reaction=reaction)
            newReaction.save()
        return redirect('/blog/' + str(blogId))
    else:
        return redirect('/login')


@csrf_exempt
def comment(request, blogId):
    if request.session.get('user'):
        email = request.session['user']['email']
        if (request.method == 'POST'):
            user = User.objects.get(email=email)
            blog = Blog.objects.get(id=blogId)
            content = request.POST.get('content')
            if content:
                # Create new comment
                newComment = Comment(
                    iduser=user, idblog=blog, content=content)
                newComment.save()
            return redirect('/blog/' + str(blogId))
        elif (request.method == 'DELETE'):
            user = User.objects.get(email=email)
            blog = Blog.objects.get(id=blogId)
            commentId = request.POST.get('commentId')
            # Check if the user is the author of the comment
            comment = Comment.objects.get(id=commentId)
            if comment.iduser == user:
                comment.delete()
            return redirect('/blog/' + str(blogId))
        elif (request.method == 'PUT'):
            user = User.objects.get(email=email)
            blog = Blog.objects.get(id=blogId)
            commentId = request.POST.get('commentId')
            content = request.POST.get('content')
            # Check if the user is the author of the comment
            comment = Comment.objects.get(id=commentId)
            if comment.iduser == user:
                comment.content = content
                comment.save()
            return redirect('/blog/' + str(blogId))
        else:
            return redirect('/blog/' + str(blogId))
    else:
        return redirect('/login')


def about(request):
    userCount = User.objects.count()
    blogCount = Blog.objects.count()
    collectionCount = Collection.objects.count()
    commentCount = Comment.objects.count()
    reactionCount = Reaction.objects.count()
    return render(request, 'pages/about.html', {'userCount': userCount, 'blogCount': blogCount,
                                                'collectionCount': collectionCount, 'commentCount': commentCount,
                                                'reactionCount': reactionCount})


def more(request):
    # get all name collection
    collections = Collection.objects.all()
    # get all users have blogged
    users = User.objects.filter(blogs__isnull=False).distinct()
    return render(request, 'pages/viewmore.html', {'collections': collections, 'users': users})


def conllection(request, id):
    try:
        # get collection by id
        collection = Collection.objects.get(id=id)
        # get all blogs in collection
        blogs = Blog.objects.filter(collectionId=collection)
    except Collection.DoesNotExist:
        # naviagte to error.html
        raise Http404("Collection không tồn tại")
    return render(request, 'pages/collection.html', {'blogs': blogs, 'collection': collection})


def createBlog(request):
    if request.session.get('user'):
        if request.method == 'POST':
            user = User.objects.get(email=request.session['user']['email'])
            collection_ids = request.POST.getlist('collection')
            collections = Collection.objects.filter(id__in=collection_ids)
            title = request.POST.get('title').strip()
            content = request.POST.get('content').strip()
            image = request.FILES.get('image')
            result = blogValidate(title, content, image, collections)
            if result['success'] == False:
                messages.error(request, result['message'])
                collections = Collection.objects.all()
                return redirect('/create', {'collections': collections})
            # # create new blog
            newBlog = Blog(userid=user, title=title,
                           content=content, image=image)
            newBlog.save()
            # add collection to blog
            newBlog.collectionId.set(collections)
            # Send message success and clear form
            messages.success(request, 'Tạo blog thành công')
            return redirect('/create')
        # Get all collections
        collections = Collection.objects.all()
        return render(request, 'pages/blog/createBlog.html', {'collections': collections})
    else:
        return redirect('/login')


def editBlog(request, id):
    user = User.objects.get(email=request.session['user']['email'])
    blogOwner = Blog.objects.get(id=id).userid
    if not user:
        return redirect('/login')
    if not user.isadmin or user != blogOwner:
        return redirect(reverse('blog', args=[id]))
    if request.method == 'POST':
        blog = Blog.objects.get(id=id)
        if not user.isadmin or user != blogOwner:
            return redirect('/blog/' + str(id))
        # get data from request POST
        title = request.POST.get('title').strip()
        content = request.POST.get('content').strip()
        image = request.FILES.get('image')
        collection_ids = request.POST.getlist('collection')
        collections = Collection.objects.filter(id__in=collection_ids)
        # Validate form
        result = editBlogValidate(title, content, image, collection_ids)
        if result['success'] == False:
            messages.error(request, result['message'])
            print(result['message'])
            return redirect('/blog/' + str(id) + '/edit')
        print('Validate success')
        # compare old data and new data
        if blog.title != title:
            blog.title = title
        if blog.content != content:
            blog.content = content
        if image:
            blog.image = image
        if collections != blog.collectionId.all():
            blog.collectionId.set(collections)
        # save blog
        blog.save()
        return redirect('/blog/' + str(id))
    blog = Blog.objects.get(id=id)
    collections = Collection.objects.all()
    blogCollections = blog.collectionId.all()
    return render(request, 'pages/blog/editBlog.html', {'blog': blog, 'collections': collections, 'blogCollections': blogCollections})


def profile(request, username):
    try:
        # get user infomation with username
        user = User.objects.get(username=username)
        # get all blogs of user
        blogs = Blog.objects.filter(Q(userid=user) & Q(
            status=True)).order_by('-createdat')
        # count reaction of user
        reactionCount = Reaction.objects.filter(iduser=user).count()
        # count comment of user
        commentCount = Comment.objects.filter(iduser=user).count()
    except User.DoesNotExist:
        raise Http404("Người dùng không tồn tại.")
    return render(request, "pages/profile.html",
                  {'user': user, 'blogs': blogs, 'reactionCount': reactionCount, 'commentCount': commentCount})


def editProfile(request, username):
    days = [str(day) for day in range(1, 32)]
    months = [
        ("01", "Tháng 1"),
        ("02", "Tháng 2"),
        ("03", "Tháng 3"),
        ("04", "Tháng 4"),
        ("05", "Tháng 5"),
        ("06", "Tháng 6"),
        ("07", "Tháng 7"),
        ("08", "Tháng 8"),
        ("09", "Tháng 9"),
        ("10", "Tháng 10"),
        ("11", "Tháng 11"),
        ("12", "Tháng 12"),
    ]
    years = [str(year) for year in range(1920, 2023)]
    user = User.objects.get(email=request.session['user']['email'])
    profileUser = User.objects.get(username=username)
    if not user:
        return redirect('/login')
    if user != profileUser:
        return error(request, 'Bạn không có quyền truy cập trang này')

    if request.method == 'POST':
        # get data from request POST
        firstname = request.POST.get('firstname').strip()
        lastname = request.POST.get('lastname').strip()
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        avatar = request.FILES.get('avatar')
        gender = request.POST.get('gender')
        birthday_day = request.POST.get('birthday_day')
        birthday_month = request.POST.get('birthday_month')
        birthday_year = request.POST.get('birthday_year')
        bio = request.POST.get('bio').strip()

        # Validate form
        result = editProfileValidate(firstname, lastname, username, profileUser.username, email, profileUser.email,
                                     birthday_day, birthday_month, birthday_year)
        if result['success'] == False:
            messages.error(request, result['message'])
            return redirect('/@' + username + '/edit', {'user': user, 'days': days, 'months': months, 'years': years})
        # compare old data and new data
        if profileUser.firstname != firstname:
            profileUser.firstname = firstname
        if profileUser.lastname != lastname:
            profileUser.lastname = lastname
        if profileUser.username != username:
            profileUser.username = username
        if profileUser.email != email:
            profileUser.email = email
        if avatar:
            profileUser.avatar = avatar
        if profileUser.gender != gender:
            profileUser.gender = gender
        birthday = date(int(birthday_year), int(
            birthday_month), int(birthday_day))
        if profileUser.birthday != birthday and birthday != date(1920, 1, 1):
            profileUser.birthday = birthday
        if profileUser.bio != bio:
            profileUser.bio = bio
            # save user
        profileUser.save()
        messages.success(request, 'Cập nhật thông tin thành công')
        return redirect('/@' + username + '/edit', {'user': user, 'days': days, 'months': months, 'years': years})
    return render(request, 'pages/editProfile.html', {'user': user, 'days': days, 'months': months, 'years': years})


def search(request):
    query = request.GET.get('q')
    if query:
        # check first character is @
        if query[0] == '@':
            # remove @
            query = query[1:]
            # get user by username
            results = User.objects.filter(
                Q(username__icontains=query) | Q(firstname__icontains=query) | Q(lastname__icontains=query))
        else:
            results = Blog.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query) & Q(status=True))
    else:
        results = []

    context = {
        'results': results,
        'query': query or ""
    }
    return render(request, 'pages/search.html', context)


def login(request):
    if request.method == 'POST':
        emailOrUsername = request.POST.get('email')
        password = request.POST.get('password')
        result = loginValidate(emailOrUsername, password)
        if result['success']:
            user = result['user']
            request.session['user'] = {
                'email': user.email,
                'firstName': user.firstname,
                'lastName': user.lastname,
                'username': user.username,
                'avatar': user.avatar.url,
                'admin': user.isadmin
            }
            return redirect('/')
        else:
            messages.error(request, result['message'])
            return redirect('/login')
    return render(request, 'pages/login.html')


def logout(request):
    if request.session.get('user'):
        del request.session['user']
    return redirect('/')


def register(request):
    days = [str(day) for day in range(1, 32)]
    months = [
        ("01", "Tháng 1"),
        ("02", "Tháng 2"),
        ("03", "Tháng 3"),
        ("04", "Tháng 4"),
        ("05", "Tháng 5"),
        ("06", "Tháng 6"),
        ("07", "Tháng 7"),
        ("08", "Tháng 8"),
        ("09", "Tháng 9"),
        ("10", "Tháng 10"),
        ("11", "Tháng 11"),
        ("12", "Tháng 12"),
    ]
    years = [str(year) for year in range(1920, 2023)]
    if request.method == 'POST':
        email = request.POST.get('email').lower().strip()
        password = request.POST.get('password').strip()
        password_confirm = request.POST.get('password_confirm').strip()
        firstname = request.POST.get('firstname').strip()
        lastname = request.POST.get('lastname').strip()
        username = request.POST.get('username').strip()
        gender = request.POST.get('gender')
        birthday_day = request.POST.get('birthday_day')
        birthday_month = request.POST.get('birthday_month')
        birthday_year = request.POST.get('birthday_year')

        # validate register form
        result = registerValidate(firstname, lastname, username, email, password,
                                  password_confirm, birthday_day, birthday_month, birthday_year)

        if result['success'] == False:
            messages.error(request, result['message'])
            return redirect('/register', {'days': days, 'months': months, 'years': years})
        else:
            user = User(
                firstname=firstname,
                lastname=lastname,
                username=username,
                email=email,
                password=password,
                gender=gender,
                birthday=date(int(birthday_year), int(
                    birthday_month), int(birthday_day))
            )
            user.save()
            messages.success(request, 'Đăng ký thành công.')
            return redirect('/login')
    else:
        return render(request, 'pages/register.html', {'days': days, 'months': months, 'years': years})


def error(request, exception):
    return render(request, 'pages/error.html', {'message': exception})


def random(request):
    # random 1 blog and navigate to blog detail
    blog = Blog.objects.filter(status=True).order_by('?').first()
    if blog:
        return redirect('/blog/' + str(blog.id))
    else:
        return redirect('/')


def admin(request):
    user = User.objects.get(email=request.session['user']['email'])
    if not user:
        return redirect('/login')
    if user.isadmin:
        if request.method == 'PUT':
            # update status field of blog
            blog = Blog.objects.get(id=request.POST.get('id'))
            blog.status = True
            blog.save()
            messages.success(request, 'Đã duyệt bài viết.')
            return redirect('/admin', messages)

        elif request.method == 'DELETE':
            # delete blog
            blog = Blog.objects.get(id=request.POST.get('id'))
            blog.delete()
            messages.success(request, 'Đã xóa bài viết.')
            return redirect('/admin', messages)
        blogs = Blog.objects.filter(status=False)
        return render(request, 'pages/admin.html', {'blogs': blogs})
    elif not user.isadmin:
        messages.error(request, 'Bạn không có quyền truy cập.')
        return redirect('/error', messages)
    else:
        return redirect('/login')


def ranking(request, period='tuan'):
    # 1: descending, -1: ascending
    # period: tuan, thang, nam
    order = request.GET.get('order', '1')
    if order == '1':
        order_direction = '-'
    else:
        order_direction = ''

    # define the mapping of type to query logic
    type_queries = {
        'like': {
            'query':  Blog.objects.filter(status=True, createdat__gte=get_start_date(period)).annotate(
                like_count=Count('reaction', filter=Q(
                    reaction__reaction='like')),
            ).order_by(order_direction + 'like_count')
        },

        'comment': {
            'query': Blog.objects.filter(
                status=True,
                createdat__gte=get_start_date(period)
            ).annotate(comment_count=Count('comment')).order_by(order_direction + 'comment_count')
        },
        'view': {
            'query': Blog.objects.filter(
                status=True,
                createdat__gte=get_start_date(period)
            ).order_by(order_direction + "view")
        }
    }
    # get query results for each ranking type
    blogLike = type_queries['like']['query']
    blogComment = type_queries['comment']['query']
    blogView = type_queries['view']['query']
    print(type)
    return render(request, 'pages/ranking.html', {'blogLike': blogLike, 'blogComment': blogComment, 'blogView': blogView, 'period': period, 'order': order})


def get_start_date(period):
    if period == 'tuan':
        return datetime.now() - timedelta(days=7)
    elif period == 'thang':
        return datetime.now() - timedelta(days=30)
    elif period == 'nam':
        return datetime.now() - timedelta(days=365)
    else:
        return None


def manage(request):
    user = User.objects.get(email=request.session['user']['email'])
    if not user:
        return redirect('/login')
    if request.method == 'DELETE':
        # check if user is owner of blog
        blog = Blog.objects.get(id=request.POST.get('id'))
        if blog.userid != user:
            messages.error(request, 'Bạn không có quyền xóa bài viết này.')
            return redirect('/manage', messages)
        # delete blog
        blog.delete()
        blogs = Blog.objects.filter(user=user)
        messages.success(request, 'Đã xóa bài viết.')
        return redirect('/manage', {'blogs': blogs})
    blogs = Blog.objects.filter(userid=user)
    return render(request, 'pages/manage.html', {'blogs': blogs})
