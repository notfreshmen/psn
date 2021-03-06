import os

from flask import Blueprint, render_template, redirect, request, flash, jsonify, abort, url_for
from flask_login import login_required, current_user

from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload

from amable import session, app

from amable.models.community import Community
from amable.models.community_user import CommunityUser
from amable.models.post import Post
from amable.models.post_report import PostReport
from amable.models.community_upvote import CommunityUpvote

from amable.forms.community_search_form import CommunitySearchForm
from amable.forms.community_create_form import CommunityCreateForm
from amable.forms.post_create_form import PostCreateForm
from amable.forms.post_report_form import PostReportForm
from amable.forms.comment_create_form import CommentCreateForm


from amable.utils.files import allowed_file

from werkzeug.utils import secure_filename


communities = Blueprint('communities', __name__,
                        template_folder='../templates')

s = session()


@communities.route('/communities')
def index():
    communities = session.query(Community).order_by(Community.date_created.desc()).all()

    return render_template('communities/index.html',
                           title="Communities",
                           communities=communities,
                           form=CommunitySearchForm())


@communities.route('/communities/search', methods=['GET'])
@login_required
def search():
    if 'community' in request.args:

        if len(request.args['community']) > 0:

            queryToSearch = request.args['community']

            communityList = session.query(Community).filter(
                func.lower(Community.name).like(func.lower(queryToSearch + "%"))).all()

            return jsonify(communities=[i.serialize for i in communityList])
        else:
            return jsonify(communities={})
    else:
        flash("Arguments missing")


@communities.route('/communities/<permalink>')
def show(permalink):
    community = session.query(Community).filter_by(permalink=permalink).first()

    postCreateForm = PostCreateForm()
    postCreateForm.community_id.data = community.id

    commentCreateForm = CommentCreateForm()
    postReportForm = PostReportForm()

    if not community:
        return abort(404)

    posts = session.query(Post).filter_by(
        community_id=community.id).order_by(desc(Post.date_created)).all()

    return render_template('communities/show.html',
                           community=community,
                           post_form=postCreateForm,
                           posts=posts,
                           comment_form=commentCreateForm,
                           report_form=postReportForm)


@communities.route('/communities/new', methods=['GET'])
@login_required
def new():
    return render_template('communities/new.html',
                           form=CommunityCreateForm())


@communities.route('/communities/<community_id>/vote')
@login_required
def vote_community(community_id):
    returnDict = {}

    # First lets get the community in question
    tempCommunity = session.query(Community).filter_by(id=community_id).first()

    if tempCommunity.vote(current_user):
        returnDict['success'] = True
    else:
        returnDict['success'] = False

    return jsonify(**returnDict)


@communities.route('/communities/<id>/membership')
@login_required
def membership(id):
    json = {}

    community = session.query(Community).filter_by(id=id).first()

    # See if they're already in the community
    community_user = session.query(CommunityUser).filter_by(user=current_user, community=community).first()

    # If they're not in the community, add them. Otherwise, remove them
    if community_user is None:
        community_user = CommunityUser(
            user=current_user,
            community=community
        )

        session.add(community_user)
        session.commit()

        json['action'] = 'joined'

    else:
        session.delete(community_user)
        session.commit()

        json['action'] = 'left'

    json['success'] = True

    return jsonify(**json)


@communities.route('/communities/create', methods=['POST'])
@login_required
def create():
    # banner_url = "http://dsedutech.org/images/demo/placement_banner1.jpg"
    # thumbnail_url = "http://i.imgur.com/7mo7QHW.gif"
    form = CommunityCreateForm(request.form)

    if form.validate():

        # First thing we are going to do is create a
        # Community object with the data from our form.
        community = Community(
            name=form.name.data,
            description=form.description.data,
            nsfw=form.nsfw.data
        )

        session.add(community)
        session.commit()  # we need to create a record so we have the id

        # Now we have a community with an ID. Lets create
        # a directory to upload image files to.
        community_upload_relative = 'communities/' + str(community.id)
        community_upload_url = './amable/uploads/' + community_upload_relative

        if not os.path.exists(community_upload_url):
            os.makedirs(community_upload_url)

        # Lets do checks for Banner
        if 'banner' in request.files:
            banner_file = request.files['banner']

            if banner_file.filename != '':
                if allowed_file(banner_file.filename):
                    banner_filename = 'banner_' + \
                        secure_filename(banner_file.filename)

                    # Save | Upload Banner file
                    fullPath = os.path.join(
                        community_upload_url, banner_filename)

                    banner_file.save(fullPath)

                    community.banner_url = community_upload_relative + "/" + banner_filename
                else:
                    flash('Banner file type is not allowed, could not upload', 'error')

        # Now lets do checks for Thumbnail
        if 'thumbnail' in request.files:
            thumbnail_file = request.files['thumbnail']

            if thumbnail_file.filename != '':
                if allowed_file(thumbnail_file.filename):
                    thumbnail_filename = 'thumbnail_' + \
                        secure_filename(thumbnail_file.filename)

                    # Save | Upload Thumbnail File
                    fullPath = os.path.join(
                        community_upload_url, thumbnail_filename)

                    thumbnail_file.save(fullPath)

                    community.thumbnail_url = community_upload_relative + "/" + thumbnail_filename
                else:
                    flash(
                        'Thumbnail file type is not allowed, could not upload', 'error')

        # community.banner_url = banner_url
        # community.thumbnail_url = thumbnail_url
        community.vote(current_user)
        session.commit()

        return redirect(url_for('communities.show', permalink=community.permalink))

    return redirect(url_for('communities.new'))


@communities.route('/communities/<permalink>/reports')
def reports(permalink):
    community = session.query(Community).filter_by(permalink=permalink).first()

    reports = session.query(PostReport).all()
    post_array = []

    for x in range(0, len(reports)):
        post_array.append(session.query(Post).filter_by(id=reports[x].parent_id).all())

    post_array = [val for sublist in post_array for val in sublist]
    post_array = list(set(post_array))

    return render_template('communities/reports.html', community=community, reports=reports, post_array=post_array)
