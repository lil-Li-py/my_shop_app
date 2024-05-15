import os

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# 日志配置字典
LOGGING_DIC = {
    'version': 1.0,
    'disable_existing_loggers': False,
    # 日志格式
    'formatters': {
        'simple': {
            'format': '%(asctime)s [%(name)s] %(levelname)s  %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'filters': {},
    # 日志处理器
    'handlers': {
        'console_debug_handler': {
            'level': 'DEBUG',  # 日志处理的级别限制
            'class': 'logging.StreamHandler',  # 输出到终端
            'formatter': 'simple'  # 日志格式
        },
        'customer_info_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件,日志轮转
            'filename': os.path.join(BASE_DIR, 'logs', 'customers.log'),
            'maxBytes': 1024 * 1024 * 10,  # 日志大小 10M
            'backupCount': 10,  # 日志文件保存数量限制
            'encoding': 'utf-8',
            'formatter': 'simple',
        },
        'shopkeeper_info_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件,日志轮转
            'filename': os.path.join(BASE_DIR, 'logs', 'shopkeepers.log'),
            'maxBytes': 1024 * 1024 * 10,  # 日志大小 10M
            'backupCount': 10,  # 日志文件保存数量限制
            'encoding': 'utf-8',
            'formatter': 'simple',
        },
        'item_info_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件,日志轮转
            'filename': os.path.join(BASE_DIR, 'logs', 'item.log'),
            'maxBytes': 1024 * 1024 * 10,  # 日志大小 10M
            'backupCount': 10,  # 日志文件保存数量限制
            'encoding': 'utf-8',
            'formatter': 'simple',
        },
    },
    # 日志记录器
    'loggers': {
        'customer': {  # 导入时logging.getLogger时使用的app_name
            'handlers': ['console_debug_handler', 'customer_info_handler'],  # 日志分配到哪个handlers中
            'level': 'DEBUG',  # 日志记录的级别限制
            'propagate': False,  # 默认为True，向上（更高级别的logger）传递，设置为
        },
        'shopkeeper': {
            'handlers': ['console_debug_handler', 'shopkeeper_info_handler'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'item': {
            'handlers': ['console_debug_handler', 'item_info_handler'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}


# 加载配置字典
import logging.config
logging.config.dictConfig(LOGGING_DIC)
