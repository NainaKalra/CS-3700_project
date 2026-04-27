# services/post_service.py
from models.post import Post
from models.user import User
from werkzeug.utils import secure_filename
import os
from flask import url_for, flash

class PostValidator:
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'webp'}
    MAX_CAPTION_LENGTH = 500
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB limit
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        if not filename:
            return False
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in PostValidator.ALLOWED_EXTENSIONS
    
    @staticmethod
    def validate_post_data(text, file):
        """Validate post data before creation"""
        errors = []
        
        # Check if there's any content
        if (not text or not text.strip()) and (not file or not file.filename):
            errors.append("Post must have either text or media")
        
        # Validate caption length
        if text and len(text) > PostValidator.MAX_CAPTION_LENGTH:
            errors.append(f"Caption is too long. Maximum {PostValidator.MAX_CAPTION_LENGTH} characters")
        
        # Validate file type
        if file and file.filename:
            if not PostValidator.allowed_file(file.filename):
                errors.append(f"File type not allowed. Allowed types: {', '.join(PostValidator.ALLOWED_EXTENSIONS)}")
            
            # Check file size (if file object has size attribute)
            if hasattr(file, 'content_length') and file.content_length > PostValidator.MAX_FILE_SIZE:
                errors.append(f"File too large. Maximum {PostValidator.MAX_FILE_SIZE // (1024*1024)}MB")
        
        return errors
    
    @staticmethod
    def validate_post_update(new_caption):
        """Validate post update data"""
        errors = []
        if new_caption and len(new_caption) > PostValidator.MAX_CAPTION_LENGTH:
            errors.append(f"Caption is too long. Maximum {PostValidator.MAX_CAPTION_LENGTH} characters")
        return errors


class PostService:
    
    @staticmethod
    def create_post(user_id, text, file, upload_folder):
        """
        Create a new post with media handling
        
        Args:
            user_id: ID of the user creating the post
            text: Caption text for the post
            file: Uploaded file object
            upload_folder: Path to upload folder
        
        Returns:
            tuple: (post_object, errors_list) - If successful, post_object is returned and errors is None
        """
        # Validate post data
        errors = PostValidator.validate_post_data(text, file)
        if errors:
            return None, errors
        
        # Handle file upload
        image_url = None
        if file and file.filename and PostValidator.allowed_file(file.filename):
            # Secure the filename and save
            filename = secure_filename(file.filename)
            
            # Add timestamp to filename to avoid collisions
            from datetime import datetime
            name_parts = filename.rsplit('.', 1)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
            
            save_path = os.path.join(upload_folder, unique_filename)
            file.save(save_path)
            image_url = url_for('static', filename=f'uploads/{unique_filename}')
        
        # Get user from user_id
        user = User.get_by_id(user_id)
        if not user:
            return None, ["User not found. Please log in again."]
        
        # Create and save post using OOP model
        caption_text = text.strip() if text else ""
        new_post = Post(
            username=user.username, 
            image=image_url or '', 
            caption=caption_text
        )
        
        # Save to database using BaseModel method
        new_post.save_to_db()
        
        return new_post, None
    
    @staticmethod
    def get_all_posts():
        """Get all posts ordered by newest first using OOP method"""
        # Using the class method from Post model
        posts = Post.get_feed_posts()
        return posts
    
    @staticmethod
    def get_all_posts_as_dict():
        """Get all posts as dictionaries (for API responses)"""
        posts = Post.get_feed_posts()
        return [post.to_feed_dict() for post in posts]
    
    @staticmethod
    def get_user_posts(username):
        """Get posts by specific user using OOP method"""
        return Post.get_posts_by_user(username)
    
    @staticmethod
    def get_post_by_id(post_id):
        """Get a single post by ID using BaseModel method"""
        return Post.get_by_id(post_id)
    
    @staticmethod
    def update_post_caption(post_id, new_caption):
        """Update a post's caption using OOP encapsulation"""
        # Validate the new caption
        errors = PostValidator.validate_post_update(new_caption)
        if errors:
            return False, errors
        
        # Get the post and update
        post = Post.get_by_id(post_id)
        if not post:
            return False, ["Post not found"]
        
        # Use the model's encapsulated method
        success = post.update_caption(new_caption)
        if success:
            return True, None
        return False, ["Failed to update caption"]
    
    @staticmethod
    def delete_post(post_id):
        """Delete a post using BaseModel method"""
        post = Post.get_by_id(post_id)
        if post:
            post.delete_from_db()
            return True
        return False
    
    @staticmethod
    def get_recent_posts(hours=24):
        """Get posts from recent hours using OOP method"""
        return Post.get_recent_posts(hours)
    
    @staticmethod
    def search_posts(keyword):
        """Search posts by caption content"""
        if not keyword:
            return []
        
        # Using SQLAlchemy ILIKE for case-insensitive search
        posts = Post.query.filter(Post.caption.ilike(f'%{keyword}%')).order_by(Post.timestamp.desc()).all()
        return posts
    
    @staticmethod
    def get_posts_with_media():
        """Get only posts that have images/videos"""
        posts = Post.query.filter(Post.image != '').order_by(Post.timestamp.desc()).all()
        return posts
    
    @staticmethod
    def get_post_summary(post_id, length=100):
        """Get a summary of a post using encapsulated method"""
        post = Post.get_by_id(post_id)
        if post:
            return post.get_summary(length)
        return ""
    
    @staticmethod
    def get_post_statistics():
        """Get statistics about posts (for admin dashboard)"""
        total_posts = Post.query.count()
        posts_with_media = Post.query.filter(Post.image != '').count()
        posts_without_media = total_posts - posts_with_media
        
        # Get post count by user
        from sqlalchemy import func
        posts_by_user = db.session.query(
            Post.username, 
            func.count(Post.id).label('post_count')
        ).group_by(Post.username).all()
        
        return {
            'total_posts': total_posts,
            'posts_with_media': posts_with_media,
            'posts_without_media': posts_without_media,
            'posts_by_user': [{'username': u[0], 'count': u[1]} for u in posts_by_user]
        }