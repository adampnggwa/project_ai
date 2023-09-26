from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `users` (
    `user_id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `email` VARCHAR(100) NOT NULL UNIQUE,
    `token` VARCHAR(500),
    `token_expiration` DATETIME(6),
    `password` VARCHAR(564),
    `image_count` INT NOT NULL  DEFAULT 0,
    `edit_image_count` INT NOT NULL  DEFAULT 0,
    `variation_image_count` INT NOT NULL  DEFAULT 0,
    `last_generated_image_time` DATETIME(6)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `edited_images` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `image_url` VARCHAR(500) NOT NULL,
    `prompt` LONGTEXT NOT NULL,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_edited_i_users_e746363d` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `generated_images` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `image_url` VARCHAR(500) NOT NULL,
    `prompt` LONGTEXT NOT NULL,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_generate_users_6d7926a1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
