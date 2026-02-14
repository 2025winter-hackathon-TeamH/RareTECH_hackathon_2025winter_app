from flask import Flask, request, redirect, render_template, session, flash, abort, url_for
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta, datetime
import hashlib
import uuid
import re
import os

from models import User , Goal_post, Comment, ProgressPost, Reaction


# 定数定義
EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
SESSION_DAYS = 30

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', uuid.uuid4().hex)
#app.config['WTF_CSRF_ENABLED'] = False #--debug用。本番ではOFF(Flask-WTFのCSRF機能そのものをOFFのため)
app.permanent_session_lifetime = timedelta(days=SESSION_DAYS)

csrf = CSRFProtect(app)

# debug用あとで消す↓ @ポテ吉
# @app.route('/debug')
# def debug_goals():
#     rows = Goal_post.get_all()
#     return render_template('debug.html', rows=rows)

@app.route('/debug')
def debug_goals():
    rows = Goal_post.find_by_user_id(1)
    return render_template('debug.html', rows=rows)

# debug用あとで消す↑ @ポテ吉

# ルートページのリダイレクト
@app.route('/', methods=['GET'])
def index():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    return redirect(url_for('goals_post_view'))

# ログインページ表示
@app.route('/login', methods=['GET'])
def login_view():
    if session.get('user_id') is not None:
        return redirect(url_for('goals_post_view'))
    return render_template('login.html')

    
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
                return redirect(url_for('goals_post_view'))
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
        return redirect(url_for('goals_post_view'))
    return render_template('signup.html')

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

    return redirect(url_for('goals_post_view'))

#目標一覧ページの表示
@app.route('/goal-post', methods=['GET'])
def goals_post_view():
    user_id = session.get('user_id')
    total_ganba = Goal_post.sum_ganba
    total_dousita = Goal_post.sum_dousita

    if user_id is None:
        return redirect(url_for('login_view'))
    else:
        goals = Goal_post.get_all()
        for goal in goals: 
            goal['goal_created_at'] = goal['goal_created_at'].strftime('%Y-%m-%d %H:%M')
            goal['user_name'] = User.get_name_by_id(goal['user_id'])
        return render_template('post.html', goals=goals, user_id = user_id, total_ganba = total_ganba, total_dousita = total_dousita)
        
#目標投稿処理
@app.route('/goal-posts', methods=['POST'])
def create_goal_post():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    
    goal_message = request.form.get('goal_message', '').strip()
    if goal_message == '':
        flash('目標内容が空欄です','error')
        return redirect(url_for('goals_post_view'))
    
    goal_deadline = request.form.get('goal_deadline', '').strip()
    if goal_deadline == '':
        flash('達成期日が未入力です', 'error')
        return redirect(url_for('goals_post_view'))
    
    formatted_deadline = datetime.strptime(goal_deadline, '%Y-%m-%d')
    #HTMLからrequestで受け取った達成期限が文字列型なのでdatetime,nowのdatetime型に変換
    if datetime.now() > formatted_deadline:
        flash('達成期日は現在時刻より後の時間を設定してください')
        return redirect(url_for('goals_post_view'))
    
    Goal_post.create(user_id, goal_message, goal_deadline)
    flash('目標の投稿が完了しました。','success')
    return redirect(url_for('goals_post_view'))

#頑張れ！ボタン押下処理
@app.route('/goal-post/<int:goal_id>/reaction-ganba',methods=['POST'])
def reaction_ganba(goal_id):
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    
    goal_post = Goal_post.find_by_id(goal_id)
    
    if goal_post is None: 
        abort(404)
    
    if goal_post['user_id'] == user_id:
        abort(403)

    Reaction.create_reaction_ganba(user_id, goal_id)
    return redirect(url_for('goals_post_view'))

#どうしたボタン押下処理
@app.route('/goal-post/<int:goal_id>/reaction-dousita',methods=['POST'])
def reaction_dousita(goal_id):
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    
    goal_post = Goal_post.find_by_id(goal_id)
    
    if goal_post is None: 
        abort(404)
    
    if goal_post['user_id'] == user_id:
        abort(403)
        
    Reaction.create_reaction_dousita(user_id, goal_id)
    return redirect(url_for('goals_post_view'))

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
    return render_template('post_detail.html', post=post, progress_posts=progress_posts, user_id=user_id)


#goal-postに対しての達成or断念ボタン押下処理  --@sai_debug済
@app.route('/goal-post/<int:goal_id>/goal-post-result', methods=['POST'])
#@csrf.exempt #--debug用(このルートだけCSRFを無効化)
def update_goal_post_result(goal_id):
    #print("=== route debug start ===") #----debug_print
    #print(goal_id) #----debug_print(OK )

    user_id = session.get('user_id')
    
    if user_id is None:
        return redirect(url_for('login_view'))
    
    post = Goal_post.find_by_id(goal_id)
    #print(post) #----debug_print(OK)
    
    if post is None: 
        abort(404)

    #print("user_id:", user_id) #----debug_print(OK)
    #print("post_user_id:", post['user_id']) #----debug_print(OK)

    #投稿者本人か比較確認
    if post['user_id'] != user_id:
        abort(403)

    #フロントの<form>からname="result"の値("achievement" or "give_up")を取得
    result = request.form.get('result')
    #print("result:", result) #----debug_print(OK)

    #想定外の値を弾く(フロントコードミス防止策)
    if result not in ('achievement', 'give_up'):
        abort(400) #400:Bad_Request(=リクエストの内容が不正)

    #DB更新
    Goal_post.update_status(goal_id, result)
    #print("=== route end ===") #----debug_print

    #リダイレクト
    return redirect(url_for('post_progress_view', goal_id=goal_id))


# 進捗投稿処理  --@sai_debugほぼ完了
#@app.route('/posts/<int:post_id>/progress_posts', methods=['POST'])
@app.route('/goal-post/<int:goal_id>/progress-post', methods=['POST'])
#@csrf.exempt #--debug用(このルートだけCSRFを無効化)
def create_progress_post(goal_id):
    #print('--- create_progress_post START ---') #----debug_print
    #print('goal_id =', goal_id) #----debug_print
    
    user_id = session.get('user_id')
    #print('user_id =', user_id) #----debug_print
    
    if user_id is None:
        #user_id = 1  #debug_仮ユーザー(DBに存在するID)
        return redirect(url_for('login_view'))

    content = request.form.get('content', '').strip()
    #print('content =', repr(content)) #----debug_print
    
    if content == '':
        flash('投稿内容が空です','error')
        return redirect(url_for('post_progress_view', goal_id=goal_id))
    #print('CALL ProgressPost.create') #----debug_print
    ProgressPost.create(user_id, goal_id, content)

    #print('CREATE SUCCESS') #----debug_print
    flash('投稿が完了しました','success')
    return redirect(url_for('post_progress_view', goal_id=goal_id))


#progress-postに対してのreactionボタン押下処理(2種)  --@sai_debugほぼ完了
@app.route('/goal-post/<int:goal_id>/progress-post/<int:progress_id>/progress-post-reaction', methods=['POST'])
#@csrf.exempt #--debug用(このルートだけCSRFを無効化)
def update_progress_post_reaction(goal_id, progress_id):
    #print("=== route debug start ===") #----debug_print
    #print("goal_id = ", goal_id) #----debug_print(OK )
    #print("progress_id = ", progress_id) #----debug_print(OK )

    user_id = session.get('user_id')
    
    if user_id is None:
        return redirect(url_for('login_view'))
        #print("debug: forcing user_id=2") #----debug_print
        #user_id = 2 #----debug_print


    #goal_idが無ければ404エラー表示
    post = Goal_post.find_by_id(goal_id)
    #print(post) #----debug_print(OK)
    if post is None: 
        abort(404)
    
    #progress_idが無ければ404エラー表示
    progress_post = ProgressPost.find_by_id_and_goal_id(progress_id, goal_id)
    #print(progress_post) #----debug_print(OK)
    if progress_post is None: 
        abort(404)

    #print("user_id:", user_id) #----debug_print(OK)
    #print("post_user_id:", post['user_id']) #----debug_print(OK)

    #progress投稿者本人はリアクション不可
    if progress_post['user_id'] == user_id:
        abort(403)
    
    #フロント側で押下されたreaction_type_idのprogress値( 3 or 4)を変数(reaction_type_id)に格納
    #reaction_type_id = 3 …素晴らしい！
    #reaction_type_id = 4 …おい！
    reaction_type_id = request.form.get('reaction_type_id')
    #print("reaction_type_id:", reaction_type_id) #----debug_print(OK)

    #想定外の値を弾く(フロントコードミス防止策)
    if reaction_type_id not in ('3', '4'):
        abort(400) #400:Bad_Request(=リクエストの内容が不正)

    #reaction_typeを数値(=int型)へ変換
    reaction_type_id = int(reaction_type_id)

    #DB更新
    Reaction.create_progress_post(user_id, goal_id, progress_id, reaction_type_id) 
    #print("=== route end ===") #----debug_print

    #リダイレクト
    return redirect(url_for('post_progress_view', goal_id=goal_id))



# 自分の投稿一覧表示
@app.route('/my-page', methods=['GET'])
def my_page_view():
    user_id = session.get('user_id')
    total_achievement = Goal_post.sum_achievement
    total_give_up = Goal_post.sum_give_up
    if user_id is None:
        return redirect(url_for('login_view'))
    myposts = Goal_post.find_by_user_id(user_id)
    if myposts is None:
        flash('投稿している目標はありません','notpost')
        return render_template('my-page.html')
    else:
        for mypost in myposts:
            mypost['created_at'] = mypost['created_at'].strftime('%Y-%m-%d %H:%M')
            mypost['user_name'] = User.get_name_by_id(mypost['user_id'])
        return render_template('my-page.html', myposts=myposts, user_id=user_id, tatal_achievement=total_achievement, total_give_up=total_give_up)

# 頑張れ！ボタン押下処理_マイページ用
@app.route('/my-page/reaction-ganba',methods=['POST'])
def myr_ganba(goal_id):
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    Reaction.create_reaction_ganba(user_id, goal_id)
    return redirect(url_for('my_page_view'))

# どうしたボタン押下処理_マイページ用
@app.route('/my-page/reaction-dousita',methods=['POST'])
def myr_dousita(goal_id):
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_view'))
    Reaction.create_reaction_dousita(user_id, goal_id)
    return redirect(url_for('my_page_view'))

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
    return render_template('400.html'), 400

@app.errorhandler(403)
def bad_request(error):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'),404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'),500


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
