"""
Cấu hình chung — nguồn duy nhất cho JWT và các constant dùng chung.
"""
import os
import logging

logger = logging.getLogger(__name__)

JWT_SECRET: str = os.getenv('JWT_SECRET', 'default-secret-key-change-in-production')
JWT_EXPIRES_IN: str = os.getenv('JWT_EXPIRES_IN', '7d')

if JWT_SECRET == 'default-secret-key-change-in-production':
    logger.warning('JWT_SECRET chưa được đặt trong .env — không an toàn cho production!')
