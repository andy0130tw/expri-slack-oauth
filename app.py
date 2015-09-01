from flask import Flask
from flask import redirect
from flask import session
from flask import request

import SlackOAuth
import settings


app = Flask(__name__, static_url_path='/static')

@app.route('/')
def hello_world():
    return 'It works!'

@app.route('/slackapi')
def slackRoot():
    oauth_code = request.args.get('code', '')
    oauth_state = request.args.get('state', '')
    oauth_error = request.args.get('error', '')

    if oauth_code:
        if oauth_code == session.pop('_csrf_token', None):
            if oauth_error:
                return 'Oops, you denied the request: <b>{}</b>'.format(oauth_error)
            else:
                oauth_url = SlackOAuth.oauth(
                    client_id=settings.client_id,
                    client_secret=settings.client_secret,
                    code=oauth_code
                )
                s = request.get(oauth_url)
                return s.text()
        else:
            return '<b>CSRF token mismatch! Sorry!</b>'
    else:
        return 'Head for <a href="/slackapi/oauth">/slackapi/oauth</a> to try it.'

@app.route('/slackapi/oauth')
def slackOAuth():
    auth_url, csrf_token = SlackOAuth.authorize(
        client_id=settings.client_id
    )
    session['_csrf_token'] = csrf_token
    return redirect(auth_url)

if __name__ == '__main__':
    app.secret_key = settings.app_secret
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run()
