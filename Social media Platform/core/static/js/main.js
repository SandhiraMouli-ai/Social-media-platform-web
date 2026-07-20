// Helper: Get Cookie for CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue || (typeof CSRF_TOKEN !== 'undefined' ? CSRF_TOKEN : '');
}

// 1. Post Like System (AJAX)
function toggleLike(button) {
    const postId = button.getAttribute('data-post-id');
    const url = `/post/like/${postId}/`;
    const csrf = getCookie('csrftoken');

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrf,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        const countSpan = button.querySelector('.likes-count');
        countSpan.textContent = data.likes_count;
        
        if (data.liked) {
            button.classList.add('active');
            // Adding a small scale-up animation effect
            button.style.transform = 'scale(1.2)';
            setTimeout(() => button.style.transform = 'scale(1)', 150);
        } else {
            button.classList.remove('active');
        }
    })
    .catch(err => console.error('Error liking post:', err));
}

// 2. Expand/Collapse Comments Section
function toggleCommentsSection(postId) {
    const drawer = document.getElementById(`comments-drawer-${postId}`);
    if (drawer) {
        drawer.classList.toggle('hidden');
    }
}

// 3. Comment Posting System (AJAX)
function submitComment(event, form) {
    event.preventDefault();
    const postId = form.getAttribute('data-post-id');
    const input = form.querySelector('.comment-input');
    const content = input.value.trim();
    if (!content) return;

    const url = `/post/comment/${postId}/`;
    const csrf = getCookie('csrftoken');
    
    const formData = new FormData();
    formData.append('content', content);

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrf
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Append new comment HTML
            const list = document.getElementById(`comments-list-${postId}`);
            const comment = data.comment;
            
            const commentHTML = `
                <div class="comment-item">
                    <img src="${comment.profile_pic}" alt="Avatar" class="comment-avatar">
                    <div class="comment-bubble">
                        <div class="comment-user-info">
                            <span class="comment-author">${comment.author}</span>
                            <span class="comment-time">${comment.created_at}</span>
                        </div>
                        <p class="comment-text">${escapeHtml(comment.content)}</p>
                    </div>
                </div>
            `;
            
            list.insertAdjacentHTML('beforeend', commentHTML);
            
            // Update comments count
            const countSpan = document.getElementById(`comment-count-${postId}`);
            if (countSpan) {
                countSpan.textContent = data.comments_count;
            }
            
            // Clear input and scroll to bottom of comments
            input.value = '';
            list.scrollTop = list.scrollHeight;
        }
    })
    .catch(err => console.error('Error submitting comment:', err));
}

// Utility: Escape HTML string
function escapeHtml(str) {
    const div = document.createElement('div');
    div.innerText = str;
    return div.innerHTML;
}

// 4. Follow/Unfollow Widget Suggestions (AJAX)
function toggleFollow(button) {
    const profileId = button.getAttribute('data-profile-id');
    const url = `/profile/follow/${profileId}/`;
    const csrf = getCookie('csrftoken');

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrf,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.following) {
                button.textContent = 'Unfollow';
                button.classList.remove('btn-primary');
                button.classList.add('btn-secondary');
            } else {
                button.textContent = 'Follow';
                button.classList.remove('btn-secondary');
                button.classList.add('btn-primary');
            }
        }
    })
    .catch(err => console.error('Error following user:', err));
}

// 5. Follow/Unfollow on Profile Page (AJAX with stats updates)
function toggleFollowProfile(button) {
    const profileId = button.getAttribute('data-profile-id');
    const url = `/profile/follow/${profileId}/`;
    const csrf = getCookie('csrftoken');

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrf,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const followerSpan = document.getElementById('follower-count');
            if (followerSpan) {
                followerSpan.textContent = data.followers_count;
            }
            
            if (data.following) {
                button.textContent = 'Unfollow';
                button.className = 'btn btn-secondary';
            } else {
                button.textContent = 'Follow';
                button.className = 'btn btn-primary';
            }
        }
    })
    .catch(err => console.error('Error following user from profile:', err));
}

// 6. Post composer image preview
function previewImage(input) {
    const previewContainer = document.getElementById('image-preview-container');
    const previewImg = document.getElementById('image-preview');
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            previewImg.src = e.target.result;
            previewContainer.classList.remove('hidden');
        }
        
        reader.readAsDataURL(input.files[0]);
    }
}

function clearImageUpload() {
    const input = document.getElementById('image-upload');
    const previewContainer = document.getElementById('image-preview-container');
    const previewImg = document.getElementById('image-preview');
    
    if (input) input.value = '';
    if (previewContainer) previewContainer.classList.add('hidden');
    if (previewImg) previewImg.src = '#';
}

// 7. Modals: Edit Profile
function openEditModal() {
    const modal = document.getElementById('edit-profile-modal');
    if (modal) modal.classList.remove('hidden');
}

function closeEditModal() {
    const modal = document.getElementById('edit-profile-modal');
    if (modal) modal.classList.add('hidden');
}

// Edit Profile Image previews
function previewAvatar(input) {
    const preview = document.getElementById('avatar-upload-preview');
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
        }
        reader.readAsDataURL(input.files[0]);
    }
}

function previewBanner(input) {
    const preview = document.getElementById('banner-upload-preview');
    const fallback = document.getElementById('banner-upload-preview-fallback');
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            if (preview) {
                preview.src = e.target.result;
            } else if (fallback) {
                // If fallback div exists, replace it with an image element
                const img = document.createElement('img');
                img.id = 'banner-upload-preview';
                img.className = 'upload-preview-banner';
                img.src = e.target.result;
                fallback.parentNode.replaceChild(img, fallback);
            }
        }
        reader.readAsDataURL(input.files[0]);
    }
}

// 8. Inbox / Direct Messaging Logic (AJAX)
function submitChatMessage(event, form) {
    event.preventDefault();
    const username = form.getAttribute('data-chat-user');
    const input = document.getElementById('chat-message-input');
    const content = input.value.trim();
    if (!content) return;

    const url = `/messages/send/${username}/`;
    const csrf = getCookie('csrftoken');

    const formData = new FormData();
    formData.append('content', content);

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrf
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Append outgoing bubble
            const container = document.getElementById('chat-messages-box');
            const bubbleHTML = `
                <div class="message-bubble-wrapper outgoing">
                    <div class="message-bubble">
                        <p class="message-content">${escapeHtml(data.message.content)}</p>
                        <span class="message-time">${data.message.timestamp}</span>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', bubbleHTML);
            container.scrollTop = container.scrollHeight;
            input.value = '';
        }
    })
    .catch(err => console.error('Error sending message:', err));
}

// Polling new incoming messages
function pollMessages(username) {
    const url = `/messages/get/${username}/`;
    
    fetch(url)
    .then(response => response.json())
    .then(data => {
        if (data.success && data.messages.length > 0) {
            const container = document.getElementById('chat-messages-box');
            
            data.messages.forEach(msg => {
                const bubbleHTML = `
                    <div class="message-bubble-wrapper incoming">
                        <div class="message-bubble">
                            <p class="message-content">${escapeHtml(msg.content)}</p>
                            <span class="message-time">${msg.timestamp}</span>
                        </div>
                    </div>
                `;
                container.insertAdjacentHTML('beforeend', bubbleHTML);
            });
            
            container.scrollTop = container.scrollHeight;
        }
    })
    .catch(err => console.error('Error polling messages:', err));
}

// Handle responsive toggle for messaging pane
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const hasUser = urlParams.has('u');
    const inboxWrapper = document.querySelector('.inbox-wrapper');
    
    if (hasUser && inboxWrapper) {
        inboxWrapper.classList.add('chat-active');
    }
});
