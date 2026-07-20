from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Max
from .models import Profile, Post, Comment, Message

@login_required
def feed_view(request):
    posts = Post.objects.all().prefetch_related('likes', 'comments', 'comments__author')
    
    current_profile = request.user.profile
    suggestions = Profile.objects.exclude(
        Q(user=request.user) | Q(followers=current_profile)
    )[:5]
    
    return render(request, 'core/feed.html', {
        'posts': posts,
        'suggestions': suggestions,
        'active_tab': 'home'
    })

@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')
        
        if content or image:
            Post.objects.create(
                author=request.user,
                content=content,
                image=image
            )
    return redirect('feed')

@login_required
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile
    posts = user.posts.all()
    
    is_following = request.user.profile.is_following(profile)
    suggestions = Profile.objects.exclude(
        Q(user=request.user) | Q(followers=request.user.profile)
    )[:5]
    
    return render(request, 'core/profile.html', {
        'profile_user': user,
        'profile': profile,
        'posts': posts,
        'is_following': is_following,
        'suggestions': suggestions,
        'active_tab': 'profile' if user == request.user else ''
    })

@login_required
def edit_profile(request):
    if request.method == 'POST':
        profile = request.user.profile
        profile.bio = request.POST.get('bio', '').strip()
        
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        if 'banner_image' in request.FILES:
            profile.banner_image = request.FILES['banner_image']
            
        profile.save()
        return redirect('profile', username=request.user.username)
    return redirect('feed')

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes_count
    })

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            comment = Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            return JsonResponse({
                'success': True,
                'comment': {
                    'author': comment.author.username,
                    'profile_pic': comment.author.profile.profile_picture.url if comment.author.profile.profile_picture else '/static/images/default.png',
                    'content': comment.content,
                    'created_at': 'Just now'
                },
                'comments_count': post.comments_count
            })
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def follow_unfollow(request, profile_id):
    target_profile = get_object_or_404(Profile, id=profile_id)
    current_profile = request.user.profile
    
    if current_profile == target_profile:
        return JsonResponse({'success': False, 'error': 'You cannot follow yourself'}, status=400)
        
    if current_profile.is_following(target_profile):
        current_profile.unfollow(target_profile)
        following = False
    else:
        current_profile.follow(target_profile)
        following = True
        
    return JsonResponse({
        'success': True,
        'following': following,
        'followers_count': target_profile.followers.count(),
        'following_count': target_profile.following.count()
    })

@login_required
def inbox_view(request):
    current_user = request.user
    
    messages = Message.objects.filter(Q(sender=current_user) | Q(recipient=current_user))
    
    user_ids = set()
    for msg in messages:
        user_ids.add(msg.sender_id)
        user_ids.add(msg.recipient_id)
    user_ids.discard(current_user.id)
    
    chat_users = User.objects.filter(id__in=user_ids).select_related('profile')
    
    active_username = request.GET.get('u', '')
    active_chat_user = None
    chat_messages = []
    
    if active_username:
        active_chat_user = get_object_or_404(User, username=active_username)
        Message.objects.filter(sender=active_chat_user, recipient=current_user, is_read=False).update(is_read=True)
        chat_messages = Message.objects.filter(
            (Q(sender=current_user) & Q(recipient=active_chat_user)) |
            (Q(sender=active_chat_user) & Q(recipient=current_user))
        ).order_by('timestamp')
    elif chat_users.exists():
        latest_message = Message.objects.filter(Q(sender=current_user) | Q(recipient=current_user)).order_by('-timestamp').first()
        if latest_message:
            other_user = latest_message.recipient if latest_message.sender == current_user else latest_message.sender
            return redirect(f"/messages/?u={other_user.username}")
            
    return render(request, 'core/inbox.html', {
        'chat_users': chat_users,
        'active_chat_user': active_chat_user,
        'chat_messages': chat_messages,
        'active_tab': 'messages'
    })

@login_required
def send_message(request, username):
    recipient = get_object_or_404(User, username=username)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            msg = Message.objects.create(
                sender=request.user,
                recipient=recipient,
                content=content
            )
            return JsonResponse({
                'success': True,
                'message': {
                    'content': msg.content,
                    'timestamp': msg.timestamp.strftime('%I:%M %p'),
                    'sender': msg.sender.username
                }
            })
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def get_messages(request, username):
    recipient = get_object_or_404(User, username=username)
    new_messages = Message.objects.filter(sender=recipient, recipient=request.user, is_read=False)
    message_list = []
    for msg in new_messages:
        message_list.append({
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%I:%M %p'),
            'sender': msg.sender.username
        })
    new_messages.update(is_read=True)
    
    return JsonResponse({
        'success': True,
        'messages': message_list
    })

def login_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
        
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('feed')
        else:
            messages.error(request, 'Invalid username or password.')
            
    return render(request, 'core/login.html')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
        
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        
        if not username or not email or not password:
            messages.error(request, 'All fields are required.')
        elif password != password_confirm:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect('feed')
            
    return render(request, 'core/signup.html')

def logout_view(request):
    logout(request)
    return redirect('login')
