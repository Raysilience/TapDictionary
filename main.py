import logging
import argparse
from magic_finger import MagicFinger

parser = argparse.ArgumentParser(description='magic finger demo')
parser.add_argument('-v', '--verbosity', choices=['DEBUG', 'INFO', 'CRITICAL'],  help='control output verbosity')
parser.add_argument('-f', '--file',  help='input image path')
args = parser.parse_args()

if args.verbosity == 'DEBUG':
    level = logging.DEBUG
elif args.verbosity == 'INFO':
    level = logging.INFO
else:
    level = logging.CRITICAL

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=level, format=LOG_FORMAT)

img_path = './3.jpg'
if (args.file):
    img_path = args.file


mf = MagicFinger(precision=2, max_len_cn=1)
mf.set_image(img_path)

mf.draw(mode=mf.DRAWLINE | mf.INTERACTIVE)

# result = mf.translate()
# print(result)