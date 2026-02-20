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

    @classmethod
    def sum_ganba(cls, goal_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT SUM(reaction_type_id = 1) AS sum_ganba FROM reactions WHERE goal_id = %s;" 
                cur.execute(sql, (goal_id,))
                row = cur.fetchone()
                return row["sum_ganba"] or 0
        finally:
            db_pool.release(conn)
            
    @classmethod
    def sum_dousita(cls, goal_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT SUM(reaction_type_id = 2) AS sum_dousita FROM reactions WHERE goal_id = %s;" 
                cur.execute(sql, (goal_id,))
                row = cur.fetchone()
                return row["sum_dousita"] or 0
        finally:
            db_pool.release(conn)


    @classmethod
    def sum_achievement(cls, user_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT SUM(achievement_status = 'achievement') AS achievement FROM goals WHERE user_id = %s;" 
                cur.execute(sql, (user_id,))
                row = cur.fetchone()
                return row["achievement"] or 0
        finally:
            db_pool.release(conn)
            
    @classmethod
    def sum_give_up(cls, user_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT SUM(achievement_status = 'give_up') AS give_up FROM goals WHERE user_id = %s;" 
                cur.execute(sql, (user_id,))
                row = cur.fetchone()
                return row["give_up"] or 0
        finally:
            db_pool.release(conn)


    """
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
    #goal_postの達成/断念ボタン押下時のDB更新処理 @sai_debugほぼ完了
    @classmethod
    def find_by_id(cls, post_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                #SUM=0でエラーになるのを回避
                # SUM(...) → NULL
                # COALESCE(NULL, 0) → 0
                sql = """
                    SELECT g.*, 
                    COALESCE(SUM(CASE WHEN r.reaction_type_id=1 THEN 1 ELSE 0 END),0) AS ganba_count,
                    COALESCE(SUM(CASE WHEN r.reaction_type_id=2 THEN 1 ELSE 0 END),0) AS doshita_count 
                    FROM goals g 
                    LEFT JOIN reactions r ON g.id = r.goal_id
                    WHERE g.id=%s 
                    GROUP BY g.id;
                """
                cur.execute(sql, (post_id,))
                post = cur.fetchone()
            return post
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod    # マイページ一覧表示用_ポテ吉
    def find_by_user_id(cls, user_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT g.*, SUM(CASE WHEN r.reaction_type_id=1 THEN 1 ELSE 0 END) AS ganba_count, SUM(CASE WHEN r.reaction_type_id=2 THEN 1 ELSE 0 END) AS doshita_count FROM goals g LEFT JOIN reactions r ON g.id = r.goal_id WHERE g.user_id=%s GROUP BY g.id ORDER BY g.goal_created_at DESC;"
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
    #reactionボタン押下前チェック用
    def find_by_id_and_goal_id(cls, progress_id, goal_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM progresses WHERE id=%s AND goal_id=%s;"
                cur.execute(sql, (progress_id, goal_id))
                progress_post = cur.fetchone()
            return progress_post
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)
    
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

    # progress_post_reactionボタン押下用 @sai
    @classmethod
    def create_progress_post(cls, user_id, goal_id, progress_id, reaction_type_id):
        #print("create_progress_post(user_id, goal_id, progress_id, reaction_type_id):", user_id, goal_id, progress_id, reaction_type_id) #----debug_print(OK )
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "INSERT INTO reactions (user_id, goal_id, progress_id, reaction_type_id) VALUES (%s, %s, %s, %s);"
                cur.execute(sql, (user_id, goal_id, progress_id, reaction_type_id))
                #print("rowcount:", cur.rowcount) #----debug_print(OK)
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    # progress_post_reaction @sai
    @classmethod
    def count_progress_reactions(cls, progress_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT reaction_type_id, COUNT(*) as count FROM reactions WHERE progress_id=%s GROUP BY reaction_type_id ORDER BY reaction_type_id;"
                cur.execute(sql, (progress_id,))
                rows = cur.fetchall()
            
            #reaction値の初期化(reaction=0件対策)
            reaction_counts = {3:0, 4:0}
            
            #DBから取得したreaction_type_id(3 or 4)＋カウント数をreaction_countsへ格納
            #例：{"reaction_type_id": 1, "count": 5}
            for row in rows:
                reaction_counts[row["reaction_type_id"]] = row["count"]

            return reaction_counts

        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)


    # 各Posts_reaction(goal_post+progress_post)集計用 @sai
    @classmethod
    def count_posts_reactions(cls, goal_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT reaction_type_id, COUNT(*) as count FROM reactions WHERE goal_id=%s GROUP BY reaction_type_id ORDER BY reaction_type_id;"
                cur.execute(sql, (goal_id,))
                rows = cur.fetchall()
            
            #reaction値の初期化(reaction=0件対策)
            reaction_counts = {1:0, 2:0, 3:0, 4:0}
            
            #DBから取得したreaction_type_id(1-4)＋カウント数をreaction_countsへ格納
            #例：{"reaction_type_id": 1, "count": 5}
            for row in rows:
                reaction_counts[row["reaction_type_id"]] = row["count"]

            #goal_post+progress_postの応援or激励を集計
            sum_ouen    =  reaction_counts[1] + reaction_counts[3]
            sum_gekirei =  reaction_counts[2] + reaction_counts[4]
            return {

                    "sum_ouen"    : sum_ouen,
                    "sum_gekirei" : sum_gekirei
            }
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
