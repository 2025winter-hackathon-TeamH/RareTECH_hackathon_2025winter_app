from flask import Flask, request, redirect, render_template, session, flash, abort, url_for
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
import hashlib
import uuid
import re
import os

from models import User , Goal_post, Comment, ProgressPost


# 定数定義
EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
SESSION_DAYS = 30

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', uuid.uuid4().hex)
#app.config['WTF_CSRF_ENABLED'] = False #--debug用。本番ではOFF(Flask-WTFのCSRF機能そのものをOFFのため)
app.permanent_session_lifetime = timedelta(days=SESSION_DAYS)

csrf = CSRFProtect(app)
# ルートページのリダイレクト
@app.route('/', methods=['GET'])
def index():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    return redirect(url_for('post_view'))

# ログインページ表示
@app.route('/login', methods=['GET'])
def login_view():
    if session.get('user_id') is not None:
        return redirect(url_for('post_view'))
    return render_template('auth/login.html')

# ログイン処理
@app.route('/login', methods=['POST'])
def login_prossece():
    email = request.form.get('email')
    password = request.form.get('password')

    if email =='' or password =='':
        flash('&#9888;&#65039;メールアドレス or パスワードが空です','error')
    else:
        user = User.find_by_email(email)
        if user is None:
            flash('&#9888;&#65039;メールアドレス or パスワードが違います','error')
        else:
            hashPassword = hashlib.sha256(password.encode('utf-8')).hexdigest()
            if hashPassword != user['password']:
                flash('&#9888;&#65039;メールアドレス or パスワードが違います','error')
            else:
                session['user_id'] = user["id"]
                return redirect(url_for('post_view'))
    return redirect(url_for('login_view'))

# ログアウト
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_view'))

# 新規登録ページ
@app.route('/signup', methods=['GET'])
def signup_view():
    if session.get('user_id') is not None:
        return redirect(url_for('post_view'))
    return render_template('auth/signup.html')

# 新規登録処理
@app.route('/signup', methods=['POST'])
def signup_process():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    password_confirmation = request.form.get('password_confirmation', '')

    # 空チェック
    if not name or not email or not password or not password_confirmation:
        flash("&#9888;&#65039;空のフォームがあります", 'error')
        return redirect(url_for('signup_view'))
    
    # パスワード一致チェック
    if password != password_confirmation:
        flash("&#9888;&#65039;パスワードが一致しません", "error")
        return redirect(url_for('signup_view'))
    
    # メール形式チェック
    if re.match(EMAIL_PATTERN, email) is None:
        flash("&#9888;&#65039;正しいメールアドレスの形式ではありません", 'error')
        return redirect(url_for('signup_view'))
    
    # 既存ユーザーチェック
    registered_user = User.find_by_email(email)
    if registered_user is not None:
        flash("&#9888;&#65039;既に登録済みのメールアドレスです", 'error')
        return redirect(url_for('signup_view'))
    
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    user_id = User.create(name, email, hashed_password)

    session['user_id'] = user_id

    return redirect(url_for('post_view'))

#目標一覧ページの表示
@app.route('/goal-post', methods=['GET'])
def goals_post_view():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    else:
        goals = Goal_post.get_all()
        for goal in goals: 
            goal['created_at'] = goal['created_at'].strftime('%Y-%m-%d %H:%M')
            goal['user_name'] = User.get_name_by_id(goal['user_id'])

        return render_template('post/post.html', goals=goals, user_id = user_id)
    
#目標投稿処理
@app.route('/goal-posts', methods=['POST'])
def create_goal_post():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    goal_message = request.form.get('goal_message', '').strip()
    if goal_message == '':
        flash('目標内容が空欄です','error')
        return redirect(url_for('posts_view'))
    Goal_post.create(user_id, goal_message)
    flash('目標の投稿が完了しました。','success')
    return redirect(url_for('goals_post_view'))

#頑張れ！ボタン押下処理
"""
# ルートページのリダイレクト処理
@app.route('/', methods=['GET'])
def index():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    return redirect(url_for('posts_view'))


# サインアップページの表示
@app.route('/signup', methods=['GET'])
def signup_view():
    if session.get('user_id') is not None:
        return redirect(url_for('posts_view'))
    return render_template('auth/signup.html')


# サインアップ処理
@app.route('/signup', methods=['POST'])
def signup_process():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    password_confirmation = request.form.get('password_confirmation', '')

    # 空チェック
    if not name or not email or not password or not password_confirmation:
        flash("空のフォームがあります" , 'error')
        return redirect(url_for('signup_view'))

    # パスワード一致チェック
    if password != password_confirmation:
        flash('二つのパスワードの値が違っています','error')
        return redirect(url_for('signup_view'))

    # メール形式チェック
    if re.match(EMAIL_PATTERN, email) is None:
        flash('正しいメールアドレスの形式ではありません','error')
        return redirect(url_for('signup_view'))

    # 既存ユーザーチェック
    registered_user = User.find_by_email(email)
    if registered_user is not None:
        flash('既に登録されているメールアドレスです','error')
        return redirect(url_for('signup_view'))

    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    user_id = User.create(name, email, hashed_password)

    session['user_id'] = user_id

    return redirect(url_for('posts_view'))


# ログインページの表示
@app.route('/login', methods=['GET'])
def login_view():
    if session.get('user_id') is not None:
        return redirect(url_for('posts_view'))
    return render_template('auth/login.html')


# ログイン処理
@app.route('/login', methods=['POST'])
def login_process():
    email = request.form.get('email')
    password = request.form.get('password')

    if email =='' or password == '':
        flash('メールアドレスorパスワードが空です','error')
    else:
        user = User.find_by_email(email)
        if user is None:
            flash('メールアドレスorパスワードが違います','error')
        else:
            hashPassword = hashlib.sha256(password.encode('utf-8')).hexdigest()
            if hashPassword != user["password"]:
                flash('メールアドレスorパスワードが違います','error')
            else:
                session['user_id'] = user["id"]
                return redirect(url_for('posts_view'))
    return redirect(url_for('login_view'))


# ログアウト
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_view'))


# 投稿一覧ページの表示
@app.route('/post', methods=['GET'])
def posts_view():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    else:
        posts = Post.get_all()
        for post in posts:
            post['created_at'] = post['created_at'].strftime('%Y-%m-%d %H:%M')
            post['user_name'] = User.get_name_by_id(post['user_id'])

        return render_template('post/posts.html', posts=posts, user_id=user_id)


# 投稿処理
@app.route('/posts', methods=['POST'])
def create_post():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    content = request.form.get('content', '').strip()
    if content == '':
        flash('投稿内容が空です','error')
        return redirect(url_for('posts_view'))
    Post.create(user_id, content)
    flash('投稿が完了しました','success')
    return redirect(url_for('posts_view'))

# 投稿削除処理
@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))

    post = Post.find_by_id(post_id)
    if post is None:
        abort(404)

    if post['user_id'] != user_id:
        flash('この投稿を削除することはできません', 'error')
        return redirect(url_for('posts_view'))

    Post.delete(post_id)
    flash('投稿が削除されました','success')
    return redirect(url_for('posts_view'))

# 投稿詳細ページの表示
@app.route('/posts/<int:post_id>', methods=['GET'])
def post_detail_view(post_id):
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    post = Post.find_by_id(post_id)
    if post is None:
        abort(404)
    post['created_at'] = post['created_at'].strftime('%Y-%m-%d %H:%M')
    post['user_name'] = User.get_name_by_id(post['user_id'])

    comments = Comment.get_by_post_id(post_id)
    for comment in comments:
        comment['created_at'] = comment['created_at'].strftime('%Y-%m-%d %H:%M')
        comment['user_name'] = User.get_name_by_id(comment['user_id'])

    return render_template('post/post_detail.html', post=post, comments = comments, user_id=user_id)
"""

# 進捗ページの表示  --@sai
#@app.route('/post/<int:post_id>', methods=['GET'])
@app.route('/goal-post/<int:goal_id>', methods=['GET'])
def post_progress_view(goal_id):
    print(goal_id) #----debug_print(OK )

    #目標表示(1種)
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    post = Goal_post.find_by_id(goal_id)
    #print(post) #----debug_print(OK)

    if post is None: #----debug_print(OK)
        abort(404)

    post['goal_created_at'] = post['goal_created_at'].strftime('%Y-%m-%d %H:%M') #created_atから投稿日時を返す
    post['user_name'] = User.get_name_by_id(post['user_id']) #user_idから名前を返す
    #print("post =", post) #----debug_print(OK )
    #print("type(post) =", type(post)) #----debug_print(OK )
    #print(post['goal_created_at']) #----debug_print(OK )
    #print(post['user_name']) #----debug_print(OK )

    #目標ポストのリアクション数(2種)表示
    #実装未了

    #進捗一覧表示
    #Python変数（list）= Pythonクラス（モデル）.Pythonメソッド(Python変数)
    progress_posts = ProgressPost.get_by_post_id(goal_id)
    #print("progress_posts =", progress_posts) #----debug_print(OK )

    #forでdict（1レコード分）in list を回す
    for progress_post in progress_posts:
        #Pythonの辞書['辞書のキー（DBカラム名と同名）']=Pythonの辞書['辞書のキー（DBカラム名と同名）'].Pythonの日時変換
        progress_post['progress_created_at'] = progress_post['progress_created_at'].strftime('%Y-%m-%d %H:%M')
        progress_post['user_name'] = User.get_name_by_id(progress_post['user_id'])
        #print("progress_post =", progress_post) #----debug_print(OK )
        #print("type(progress_post) =", type(progress_post)) #----debug_print(OK )
        #print(progress_post['progress_created_at']) #----debug_print(OK )
        #print(progress_post['user_name']) #----debug_print(OK )
    return render_template('post/post_detail.html', post=post, progress_posts=progress_posts, user_id=user_id)

# 進捗投稿処理  --@sai_debugほぼ完了
#@app.route('/posts/<int:post_id>/progress_posts', methods=['POST'])
@app.route('/goal-post/<int:goal_id>/progress-post', methods=['POST'])
#@csrf.exempt #--debug用(このルートだけCSRFを無効化)
def create_progress_post(goal_id):
    print('--- create_progress_post START ---') #----debug_print
    print('goal_id =', goal_id) #----debug_print
    
    user_id = session.get('user_id')
    print('user_id =', user_id) #----debug_print
    
    if user_id is None:
        #user_id = 1  #debug_仮ユーザー(DBに存在するID)
        return redirect(url_for('login_view'))

    content = request.form.get('content', '').strip()
    print('content =', repr(content)) #----debug_print
    
    if content == '':
        flash('投稿内容が空です','error')
        return redirect(url_for('post_progress_view', goal_id=goal_id))
    print('CALL ProgressPost.create') #----debug_print
    ProgressPost.create(user_id, goal_id, content)

    print('CREATE SUCCESS') #----debug_print
    flash('投稿が完了しました','success')
    return redirect(url_for('post_progress_view', goal_id=goal_id))

"""
# コメント処理
@app.route('/posts/<int:post_id>/comments', methods=['POST'])
def create_comment(post_id):
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    content = request.form.get('content', '').strip()
    if content == '':
        flash('コメント内容が空です','error')
        return redirect(url_for('post_detail_view', post_id=post_id))
    Comment.create(user_id, post_id, content)
    flash('コメントの投稿が完了しました','success')
    return redirect(url_for('post_detail_view', post_id=post_id))
"""

@app.errorhandler(400)
def bad_request(error):
    return render_template('error/400.html'), 400

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error/404.html'),404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error/500.html'),500


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
