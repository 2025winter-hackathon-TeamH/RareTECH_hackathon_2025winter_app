from flask import abort
import pymysql
from util.DB import DB

# 初期起動時にコネクションプールを作成し接続を確立
db_pool = DB.init_db_pool()

# ユーザークラス
class User:
    @classmethod
    def create(cls, name, email, password): # DB寄せ済み_@sai
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "INSERT INTO users (user_name, email, password) VALUES (%s, %s, %s);"
                cur.execute(sql, (name, email, password))
                conn.commit()
                # AUTO_INCREMENT された id を返す
                return cur.lastrowid
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def find_by_email(cls, email):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM users WHERE email=%s;"
                cur.execute(sql, (email,))
                user = cur.fetchone()
            return user
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def get_name_by_id(cls, user_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT user_name FROM users WHERE id=%s;"
                cur.execute(sql, (user_id,))
                user = cur.fetchone()
            return user['user_name'] if user else None
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

# Postsクラス
# Goal_postsクラス
class Goal_post:
    @classmethod
    def get_all(cls):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM goals ORDER BY goal_created_at DESC;"
                cur.execute(sql)
                posts = cur.fetchall()
            return posts
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)
#↑はBDに寄せ済み@もりりん

    """
    @classmethod
    def create(cls, user_id, goal_message, goal_deadline):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "INSERT INTO goals (user_id, goal_message, goal_deadline) VALUES (%s, %s, %s);"
                cur.execute(sql, (user_id, goal_message, goal_deadline))
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)
    #↑はDBに寄せ済み@もりりん

    ""
    @classmethod
    def delete(cls, post_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "UPDATE goals SET deleted_at = NOW() WHERE id = %s;"
                cur.execute(sql, (post_id))
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)
    """
    
    @classmethod
    def find_by_id(cls, post_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM goals WHERE id=%s;"
                cur.execute(sql, (post_id,))
                post = cur.fetchone()
            return post
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod # マイページ一覧表示用 @ポテ吉
    def find_by_user_id(cls, user_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM goals WHERE user_id=%s;"
                cur.execute(sql, (user_id,))
                myposts = cur.fetchall()
            return myposts
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    #goal_postの達成/断念ボタン押下時のDB更新処理 @sai_debugほぼ完了
    @classmethod
    def update_status(cls, goal_id, result):
        #print("update_status called:", goal_id, result)#----debug_print(OK)
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "UPDATE goals SET achievement_status = %s WHERE id = %s;"
                cur.execute(sql, (result, goal_id))
                #print("rowcount:", cur.rowcount)#----debug_print(OK)
                conn.commit()
        except pymysql.Error as e:
            conn.rollback() #エラー発生時のトランザクションroll-back処理
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

# progress_Posts(進捗投稿)クラス @sai
class ProgressPost:
    """
    # 使わない可能性大(get_by_post_idで一覧取得のため)
    @classmethod
    def get_all(cls):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                #sql = "SELECT * FROM progresses WHERE  deleted_at IS NULL ORDER BY created_at DESC;"
                sql = "SELECT * FROM progresses WHERE  ORDER BY created_at DESC;"
                cur.execute(sql)
                posts = cur.fetchall()
            return progress_posts
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)
    """
    @classmethod
    def create(cls, user_id, goal_id, content): #-@sai_debugほぼ完了
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "INSERT INTO progresses (user_id, goal_id, progress_message) VALUES (%s, %s, %s);"
                cur.execute(sql, (user_id, goal_id, content))
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    """
    # 使わない可能性大(delete機能実装予定なしのため)
    @classmethod
    def delete(cls, post_id): 
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "UPDATE progresses SET deleted_at = NOW() WHERE id = %s;"
                cur.execute(sql, (post_id))
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def find_by_goal_id(cls, goal_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM goals WHERE id=%s AND deleted_at IS NULL;"
                cur.execute(sql, (goal_id,))
                goal_id = cur.fetchone()
            return goal_id
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)
    """
    @classmethod
    def get_by_post_id(cls, goal_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM progresses WHERE goal_id=%s ORDER BY progress_created_at DESC;"
                cur.execute(sql, (goal_id,))
                progress_posts = cur.fetchall()
            return progress_posts
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)


# Posts_reaction(goal_post+progress_post)クラス @sai
class PostReaction:
    @classmethod
    def create_progress_reaction(cls, user_id, progress_id, reaction_type_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "INSERT INTO reactions (user_id, progress_id, reaction_type_id) VALUES (%s, %s, %s);"
                cur.execute(sql, (user_id, progress_id, reaction_type_id))
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

class Reaction:
    @classmethod
    def create_reaction_ganba(cls, user_id, goal_id):
        ganbare = 1
        reaction_type_id = ganbare
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "INSERT INTO reactions (user_id, goal_id, reaction_type_id) VALUES(%s, %s, %s);"
                cur.execute(sql, (user_id, goal_id, reaction_type_id))
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def create_reaction_dousita(cls, user_id, goal_id):
        dousita = 2
        reaction_type_id = dousita
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "INSERT INTO reactions (user_id, goal_id, reaction_type_id) VALUES(%s, %s, %s);"
                cur.execute(sql, (user_id, goal_id, reaction_type_id))
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

# Commentクラス
class Comment:
    @classmethod
    def create(cls, user_id, post_id, content):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "INSERT INTO comments (user_id, post_id, content) VALUES (%s, %s, %s);"
                cur.execute(sql, (user_id, post_id, content))
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)
    @classmethod
    def get_by_post_id(cls, post_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM comments WHERE post_id=%s ORDER BY created_at DESC;"
                cur.execute(sql, (post_id,))
                comments = cur.fetchall()
            return comments
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)
