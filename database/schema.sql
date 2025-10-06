-- 创建一个名为 users 的表，如果不存在则创建
CREATE TABLE IF NOT EXISTS users (
    -- 用户ID：无符号整型，自增，主键
    -- UNSIGNED：不能为负数
    -- AUTO_INCREMENT：每插入一条数据自动 +1
    -- PRIMARY KEY：主键（唯一标识一条记录）
    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,   

    -- 用户名：最长100字符，不能为空，必须唯一
    -- UNIQUE：保证唯一性，同时会自动建立唯一索引，加快查询
    username VARCHAR(100) NOT NULL UNIQUE,                 

    -- 邮箱：最长255字符，不能为空，必须唯一
    -- UNIQUE：防止同一个邮箱被多次注册，也用于快速查询
    email VARCHAR(255) NOT NULL UNIQUE,                    

    -- 密码哈希值：存储加密后的密码（如 bcrypt/argon2），不能为 NULL
    password_hash VARCHAR(255) NOT NULL,                   

    -- 账号状态：1 表示启用，0 表示禁用
    -- TINYINT(1)：占1字节，常用于布尔值
    -- DEFAULT 1：默认启用
    is_active TINYINT(1) NOT NULL DEFAULT 1,               

    -- 最近一次登录时间
    -- DATETIME：存储日期和时间（到秒）
    -- DEFAULT NULL：默认是 NULL，表示从未登录过
    last_login DATETIME DEFAULT NULL,                      

    -- 记录创建时间
    -- TIMESTAMP：时间戳类型
    -- DEFAULT CURRENT_TIMESTAMP：插入时自动填入当前时间
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 

    -- 记录更新时间
    -- DEFAULT CURRENT_TIMESTAMP：插入时自动填入当前时间
    -- ON UPDATE CURRENT_TIMESTAMP：每次更新行时自动刷新
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) 
-- 存储引擎 InnoDB：支持事务、行级锁、外键
ENGINE=InnoDB 
-- 字符集 utf8mb4：支持所有 Unicode 字符（包括表情符号）
DEFAULT CHARSET=utf8mb4;

-- tasks 表：存储用户任务信息（核心任务）
CREATE TABLE IF NOT EXISTS tasks (
    -- 任务ID：无符号整型，自增，主键
    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    -- 关联用户ID：无符号整型，不能为空,任务必须有主人
    user_id INT UNSIGNED NOT NULL,
    -- 任务标题：最长255字符，不能为空
    title VARCHAR(255) NOT NULL,
    -- 任务描述：文本类型，可以为空
    description TEXT,
    -- 任务状态：'todo'（待办）、'in_progress'（进行中）、'completed'（已完成）、 'archived'（已归档）
    status TINYINT NOT NULL DEFAULT 0 COMMENT '0: todo, 1: in_progress, 2: completed, 3: archived',
    -- 任务优先级：'low'（低）、'medium'（中）、'high'（高）、 'urgent'（紧急）
    priority TINYINT NOT NULL DEFAULT 1 COMMENT '0: low, 1: medium, 2: high, 3: urgent',
    -- 任务截止日期，可以为空（没有截止日期）
    due_date DATETIME DEFAULT NULL,
    -- 软删除标志位：1 表示已删除，0 表示未删除（便于误删除的恢复）
    is_deleted TINYINT(1) NOT NULL DEFAULT 0,
    -- 记录创建时间
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- 记录最后一次更新时间
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    -- 外键约束，确保 user_id 必须存在于 users 表中
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    -- 为 user_id和status 创建联合索引，加快基于用户的任务查询
    INDEX idx_user_status (user_id, status),
    -- 为 due_date 创建索引，加快基于截止日期的查询或排序
    INDEX idx_due_date (due_date)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- tags 表：存储任务标签信息（用户隔离）
CREATE TABLE IF NOT EXISTS tags (
    -- 标签ID：无符号整型，自增，主键
    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    -- 关联用户ID：无符号整型，不能为空,标签必须有主人
    user_id INT UNSIGNED NOT NULL,
    -- 标签名称：最长256字符，不能为空
    name VARCHAR(256) NOT NULL,
    -- 记录创建时间
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- 联合索引，确保同一用户不能有重复标签
    UNIQUE INDEX idx_user_tag (user_id, name),
    -- 外键约束，确保 user_id 必须存在于 users 表中
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- task_tags 表：多对多关联任务和标签
CREATE TABLE IF NOT EXISTS task_tags (
    -- 任务ID：无符号整型，不能为空，存放任务的ID
    task_id INT UNSIGNED NOT NULL,
    -- 标签ID：无符号整型，不能为空，存放标签的ID
    tag_id INT UNSIGNED NOT NULL,
    -- 联合主键，确保同一任务不能重复关联同一标签
    PRIMARY KEY (task_id, tag_id),
    -- 外键约束，确保 task_id 必须存在于 tasks 表中
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    -- 外键约束，确保 tag_id 必须存在于 tags 表中
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;