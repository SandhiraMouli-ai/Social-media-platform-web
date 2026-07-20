import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialup.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Profile, Post, Comment, Message

def populate():
    print("Populating database...")
    
    # 1. Create Users
    users_data = [
        {'username': 'alice', 'email': 'alice@socialup.com', 'password': 'password123', 'bio': 'Tech lover & interface designer. Let\'s connect!'},
        {'username': 'bob', 'email': 'bob@socialup.com', 'password': 'password123', 'bio': 'Product developer. Building the future of social networks.'},
        {'username': 'charlie', 'email': 'charlie@socialup.com', 'password': 'password123', 'bio': 'Software engineer exploring clean coding practices.'}
    ]
    
    users = {}
    for u_data in users_data:
        user, created = User.objects.get_or_create(
            username=u_data['username'],
            email=u_data['email']
        )
        if created:
            user.set_password(u_data['password'])
            user.save()
            print(f"Created user: {user.username}")
        else:
            print(f"User {user.username} already exists.")
        
        # Update bio on auto-created profile
        profile = user.profile
        profile.bio = u_data['bio']
        profile.save()
        users[user.username] = user

    alice = users['alice']
    bob = users['bob']
    charlie = users['charlie']

    # 2. Setup Follow relations
    print("Setting up follow connections...")
    # Alice follows Bob and Charlie
    alice.profile.follow(bob.profile)
    alice.profile.follow(charlie.profile)
    # Bob follows Alice
    bob.profile.follow(alice.profile)
    # Charlie follows Bob
    charlie.profile.follow(bob.profile)
    
    alice.profile.save()
    bob.profile.save()
    charlie.profile.save()

    # 3. Create Posts
    print("Creating sample posts...")
    post1, created = Post.objects.get_or_create(
        author=alice,
        content="Welcome to SocialUp! Loving the glassmorphic dark mode interface. 💫🚀"
    )
    post2, created = Post.objects.get_or_create(
        author=bob,
        content="Just launched the first version of SocialUp. Fully responsive, clean gradients, and live AJAX comments/likes. Give it a spin!"
    )
    post3, created = Post.objects.get_or_create(
        author=charlie,
        content="Pair programming with Django is so satisfying. The database model system is extremely clean."
    )

    # 4. Likes
    print("Adding likes...")
    post1.likes.add(bob, charlie)
    post2.likes.add(alice, charlie)
    post3.likes.add(bob)

    # 5. Comments
    print("Adding comments...")
    Comment.objects.get_or_create(
        post=post1,
        author=bob,
        content="Welcome, Alice! Happy to have you here."
    )
    Comment.objects.get_or_create(
        post=post1,
        author=charlie,
        content="Glad you like the dark mode styling! We worked hard on the colors."
    )
    Comment.objects.get_or_create(
        post=post2,
        author=alice,
        content="This feels extremely premium and fast. The animations are so smooth!"
    )

    # 6. Sample Messages
    print("Adding direct messages...")
    Message.objects.get_or_create(
        sender=bob,
        recipient=alice,
        content="Hey Alice! Thanks for joining SocialUp. Let me know if you have any feedback on the design!"
    )
    Message.objects.get_or_create(
        sender=alice,
        recipient=bob,
        content="Hey Bob! I absolutely love the gradients and subtle blurs. The direct messaging interface looks stunning!"
    )
    Message.objects.get_or_create(
        sender=bob,
        recipient=alice,
        content="Awesome! I'm planning to add photo sharing to messages soon too."
    )
    
    print("Database population complete!")

if __name__ == '__main__':
    populate()
