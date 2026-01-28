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
        goal_created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
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
        progress_created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        goal_id INT UNSIGNED NOT NULL,
        user_id INT UNSIGNED NOT NULL,
        PRIMARY KEY (id),
        KEY idx_progresses_goal_id (goal_id),
        KEY idx_progresses_user_id (user_id),
        CONSTRAINT fk_progresses_goals FOREIGN KEY (goal_id) REFERENCES goals (id),
        CONSTRAINT fk_progresses_users FOREIGN KEY (user_id) REFERENCES users (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE
    reactions(
        id INT UNSIGNED NOT NULL AUTO_INCREMENT,
        user_id INT UNSIGNED NOT NULL,
        goal_id INT UNSIGNED ,
        progress_id INT UNSIGNED,
        reaction_type_id INT UNSIGNED NOT NULL,
        CONSTRAINT chk_not_both_null_or_not_null CHECk (
            NOT (goal_id IS NULL AND progress_id IS NULL) --両方NULLは×
            AND
            NOT (goal_id IS NOT NULL AND progress_id IS NOT NULL) --両方値ありも×
        ),
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

CREATE TABLE
    reaction_types(
        id INT UNSIGNED NOT NULL,
        reaction_type ENUM ('goal','progress') NOT NULL,
        comment TEXT NOT NULL,
        PRIMARY KEY (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
