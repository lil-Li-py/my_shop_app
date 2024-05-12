import os
from core.src_start import run
from db.db_handler import init_data


if __name__ == '__main__':
    if not os.listdir('db/data'):
        init_data()
    run()
