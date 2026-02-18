DROP DATABASE IF EXISTS snsapp;

DROP USER IF EXISTS 'testuser'@'%';


CREATE USER 'testuser'@'%' IDENTIFIED BY 'testuser';

CREATE DATABASE IF NOT EXISTS snsapp
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;


GRANT ALL PRIVILEGES ON snsapp.* TO 'testuser'@'%';

FLUSH PRIVILEGES;

USE snsapp;

CREATE TABLE
    users (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT,
        user_name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        PRIMARY KEY (id),
        UNIQUE KEY uq_users_user_name (user_name),
        UNIQUE KEY uq_users_email (email)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE
    goals (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT,
        goal_message TEXT NOT NULL,
        goal_created_at DATETIME (6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
        goal_deadline DATETIME (6) NOT NULL,
        achievement_status ENUM ('achievement','give_up'),
        user_id INT UNSIGNED NOT NULL,
        PRIMARY KEY (id),
        KEY idx_goals_user_id (user_id),
        CONSTRAINT fk_goals_users FOREIGN KEY (user_id) REFERENCES users (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE
    progresses (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT,
        progress_message TEXT NOT NULL,
        progress_created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) NOT NULL,
        goal_id INT UNSIGNED NOT NULL,
        user_id INT UNSIGNED NOT NULL,
        PRIMARY KEY (id),
        KEY idx_progresses_goal_id (goal_id),
        KEY idx_progresses_user_id (user_id),
        CONSTRAINT fk_progresses_goals FOREIGN KEY (goal_id) REFERENCES goals (id),
        CONSTRAINT fk_progresses_users FOREIGN KEY (user_id) REFERENCES users (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;


CREATE TABLE
    reaction_types(
        id INT UNSIGNED NOT NULL,
        reaction_type ENUM ('goal','progress') NOT NULL,
        comment TEXT NOT NULL,
        PRIMARY KEY (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;


CREATE TABLE
    reactions(
        id INT UNSIGNED NOT NULL AUTO_INCREMENT,
        user_id INT UNSIGNED NOT NULL,
        goal_id INT UNSIGNED NOT NULL,
        progress_id INT UNSIGNED,
        reaction_type_id INT UNSIGNED NOT NULL,
        /*
            CONSTRAINT chk_not_both_null_or_not_null CHECK (
                NOT (goal_id IS NULL AND progress_id IS NULL) 
                AND
                NOT (goal_id IS NOT NULL AND progress_id IS NOT NULL) 
            ),
        */
        PRIMARY KEY (id),
        KEY idx_reactions_user_id (user_id),
        KEY idx_reaction_goal_id (goal_id),
        KEY idx_reaction_progress_id (progress_id),
        KEY idx_reaction_reaction_type_id (reaction_type_id),
        CONSTRAINT fk_reactions_users FOREIGN KEY (user_id) REFERENCES users (id),
        CONSTRAINT fk_reactions_goals FOREIGN KEY (goal_id) REFERENCES goals (id),
        CONSTRAINT fk_reactions_progresses FOREIGN KEY (progress_id) REFERENCES progresses (id),
        CONSTRAINT fk_reactions_reaction_types FOREIGN KEY (reaction_type_id) REFERENCES reaction_types (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

INSERT INTO reaction_types (id, reaction_type, comment)
VALUES 
  (1, 'goal', '頑張れ！'),
  (2, 'goal', 'どうした？'),
  (3, 'progress', '素晴らしい！'),
  (4, 'progress', '根性見せろ！');


/* サンプルデータ */
/* password = test1234 */
INSERT INTO users (user_name, email, password)
VALUES 
  ('山田太郎', 'taro@example.com', '937e8d5fbb48bd4949536cd65b8d35c426b80d2f830c5c308e2cdec422ae2244'),
  ('鈴木二郎', 'jiro@example.com', '937e8d5fbb48bd4949536cd65b8d35c426b80d2f830c5c308e2cdec422ae2244'),
  ('田中一郎', 'ichiro@example.com', '937e8d5fbb48bd4949536cd65b8d35c426b80d2f830c5c308e2cdec422ae2244'),
  ('佐藤花子', 'hanaco@example.com', '937e8d5fbb48bd4949536cd65b8d35c426b80d2f830c5c308e2cdec422ae2244'),
  ('team_H', 'team_h@example.com', '937e8d5fbb48bd4949536cd65b8d35c426b80d2f830c5c308e2cdec422ae2244');

INSERT INTO goals (goal_message, goal_created_at, goal_deadline, achievement_status, user_id)
VALUES 
  ('11月中に旅行に行く', '2025-09-03 01:03:24', '2025-11-30 00:00:00', NULL, 1),
  ('１２月までに３キロやせる', '2025-10-10 16:11:08', '2025-12-31 00:00:00', NULL, 3),
  ('７月までに１つ資格を取る', '2026-01-01 07:34:29', '2026-06-30 00:00:00', NULL, 1),
  ('今月は早く寝る', '2026-01-01 23:59:00', '2026-01-31 00:00:00', 'give_up', 2),
  ('いいサンプルデータが思いつきませんでした', '2026-01-01-00:00:00', '2026-01-31 00:00:00', 'achievement', 4),
  ('ハッカソン入門コース完走', '2026-01-06-00:00:00', '2026-02-28 00:00:00', NULL, 5);

INSERT INTO progresses (progress_message, progress_created_at, goal_id, user_id)
VALUES 
  ('行先選定中', '2025-09-10 20:49:02', 1, 1),
  ('今から出発', '2025-11-15 08:11:47', 1, 1),
  ('１キロ瘦せた', '2025-10-31 19:20:44', 2, 3),
  ('なぜかプラス５キロ…', '2025-10-31 19:20:45', 2, 3),
  ('さっそく資格試験に申し込んだ！', '2026-01-04 21:06:09', 3, 1),
  ('フロントエンドのhtmlページ作成完了', '2026-02-13 01:00:00', 6, 5),
  ('バックエンド機能作成完了', '2026-02-15 02:00:00', 6, 5);

INSERT INTO reactions (user_id, goal_id, progress_id, reaction_type_id)
VALUES 
  (2, 1, NULL, 1),
  (3, 1, 1, 3),
  (4, 1, 2, 3),
  (1, 2, NULL, 1),
  (4, 2, 4, 4),
  (4, 2, NULL, 2);
