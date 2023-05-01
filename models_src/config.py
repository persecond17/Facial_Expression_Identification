import os

cwd = os.path.basename(os.getcwd())
ROOT = '..' if cwd == 'models_src' else '.'

TRAINING_DIR = os.path.join(ROOT, '../data/train')
VAL_TEST_DIR = os.path.join(ROOT, '../data/test')

MODEL_PATH_v01 = os.path.join(ROOT, 'models/fer_cnn_v01.pth')
MODEL_PATH_v02 = os.path.join(ROOT, 'models/fer_cnn_v02.pth')
MODEL_PATH_v03 = os.path.join(ROOT, 'models/fer_cnn_v03.pth')

