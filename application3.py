#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read classmates data from json, display as full list, by group or as individual page.
   Also allows to collect missing information about classmates FB ids. 
"""


from flask import Flask, render_template, session, request, url_for, redirect
from operator import itemgetter

from flask_oauthlib.client import OAuth, OAuthException, OAuthResponse
from config import FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, FACEBOOK_CALLBACK

from classmates import Classmates
my_class = Classmates()

application = Flask("application")

MAIN_PAGE_TEMPLATE  = "table.html"
GROUP_PAGE_TEMPLATE = "group.html"
USER_PAGE_TEMPLATE  = "user.html"

# FB auth setup
oauth = OAuth()

facebook = oauth.remote_app(
    'facebook',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'public_profile'},
    base_url='https://graph.facebook.com',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    access_token_method='GET',
    authorize_url='https://www.facebook.com/dialog/oauth'
)
        
@application.route("/")
def hello():
    return render_template(MAIN_PAGE_TEMPLATE, persons=my_class.get_people())

    
@application.route('/user/<username>')
def show_user_profile(username):         
    if username in my_class.get_translit_names():
        p = my_class.get_user(username)
        session['username'] = username
        return render_template(USER_PAGE_TEMPLATE, person=p)        
    else:
        return 'Cannot find %s' % username

@application.route('/group/<int:group_n>')
def show_post(group_n):
    if group_n in [x for x in range(401,412)]:
        return render_template(GROUP_PAGE_TEMPLATE, persons=get_group_list(group_n))
    else:
        return 'Illegal group number: %d' % group_n
    

# ---- FACEBOOK ----
@application.route('/oauth/authorize/facebook', methods=['GET', 'POST'])
def oauth_authorize_facebook():
    return facebook.authorize(callback=FACEBOOK_CALLBACK)


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('facebook_token')


@application.route('/oauth/callback/facebook/', methods=['GET', 'POST'])
def oauth_authorized_fb():
    next_url = request.args.get('next') or url_for('hello')
    resp = facebook.authorized_response()

    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )

    if isinstance(resp, OAuthException):
        return 'OAuthException: %s' % resp.message

    session['facebook_token'] = (resp['access_token'], '')
    me = facebook.get('/me?fields=id')
    u_id = me.data['id']

    url = "https://www.facebook.com/" + u_id
    p = pick_user_by_translit(session['username'])
    p['url'] = url

    new_data = [user if user['translit']!=session['username'] else p for user in PEOPLE]

    with open('classmates.json', 'w+') as outfile:
        json.dump(new_data, outfile)

    return redirect(next_url)


if __name__ == "__main__":
    print("""TODO:
    Major:
    - collect missing FB id information    
    - data collection scripts 
    - redeploy from git directory with new requirements.txt        
    
    Minor:
    - add 401...411 to list/group view + all buttons
    
    Soon:
    - big like button FS
    - store and show person's photo
    - domain name      
    - linkedin, vkontakte links
    - nice htmls overall and template structure
    - testing
    
    Not soon:
    - extendible to other MSU Econ classes
    - storing personal information securely
    
    """)

    application.secret_key = 'super secret key'
    application.run(debug = True)


