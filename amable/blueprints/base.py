from pprint import pprint

from flask import Blueprint
from flask import render_template, flash, send_from_directory, request

from flask_login import current_user

from amable.forms.user_create_form import UserCreateForm
from amable.forms.post_create_form import PostCreateForm
from amable.forms.comment_create_form import CommentCreateForm

from amable import session

from amable.services.feed_service import FeedService
from amable.forms.login_form import LoginForm


base = Blueprint('base', __name__, template_folder='../templates/base')


@base.route('/')
def index():
    if current_user.is_authenticated:
        post_form = PostCreateForm()
        user_communities = current_user.get_communities()
        post_form.community_select.choices = [
            (c.id, c.name) for c in user_communities]

        comment_form = CommentCreateForm()

        service = FeedService(user=current_user)

        requested_feed = request.args.get('feed')

        if requested_feed == 'users':
            posts = service.users()
            feed_type = 'users'
        elif requested_feed == 'top':
            posts = service.top()
            feed_type = 'top'
        else:
            posts = service.communities()
            feed_type = 'communities'

        return render_template('index.html', posts=posts, post_form=post_form, feed_type=feed_type, comment_form=comment_form)

    login_form = LoginForm()

    return render_template('index.html', login_form=login_form)


@base.route('/ui')
def ui():
    return render_template('ui.html', title="UI Guide")


@base.route('/uploads/<path:path>')
def serve_upload(path):
    print(path)

    return send_from_directory('uploads/', path)
