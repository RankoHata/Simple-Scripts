import os
import logging
import argparse
from PIL import Image

logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser(
    description='Resize Image...'
)

parser.add_argument('-s', '--source', dest='source', nargs='*', help='All Source File Path.')
parser.add_argument('-d', '--destination', dest='destination', action='store', help='Destination directory for new files.')
# parser.add_argument('-x', '--width', dest='width', action='store')
# parser.add_argument('-y', '--height', dest='height', action='store')
parser.add_argument('--size', dest='size', action='store', help='width and height')


class ResizeImg(object):
    def __init__(self, source, destination, size):
        self.source = source
        self.destination = self.get_destination(destination)
        self.size = self.get_size(size)
    
    def yield_source(self):
        for item in self.source:
            abs_path = os.path.abspath(item)
            if os.path.isdir(abs_path):
                for file_path in os.listdir(abs_path):
                    if file_path.endswith(('png', 'jpg')):
                        yield file_path
            elif os.path.isfile(abs_path):
                if abs_path.endswith(('png', 'jpg')):
                    yield abs_path

    def resize_img(self, file_path):
        filename = os.path.basename(file_path)
        img = Image.open(file_path)
        img = img.resize(self.size, Image.ANTIALIAS)
        img.save(os.path.join(self.destination, 'size_{}_'.format(self.size) + filename))
    
    @staticmethod
    def get_size(size_str):
        if size_str.startswith('(') and size_str.endswith(')'):
            try:
                tmp_left, tmp_right = size_str.split(',')
                width = int(tmp_left.strip().replace('(', ''))
                height = int(tmp_right.strip().replace(')', ''))
            except:
                raise
            else:
                return (width, height)
        elif size_str.endswith('%'):
            pass
        elif int(size_str):
            pass
        else:
            logging.error('The format of size is wrong: {}'.format(size_str))
            exit(1)

    @staticmethod
    def get_destination(destination):
        destination = os.path.abspath(destination)
        if not os.path.exists(destination):
            try:
                os.makedirs(destination)
            except:
                logging.error('Error creating destination directory: {}'.format(destination))
                raise
        return destination


def ratio_resize():
    pass


# def parse_size_args(size_str):  # 3种策略
#     if size_str.startswith('(') and size_str.endswith(')'):
#         pass
#     elif size_str.endswith('%'):
#         pass
#     elif int(size_str):
#         pass


# def main(args):
#     destination = get_destination(args)
#     size = tuple(int(i) for i in args.size)
#     if destination is None:
#         destination = os.path.abspath(os.curdir)
#     for item in args.source:
#         print(item)
#         abs_path = os.path.abspath(item)
#         if os.path.isdir(abs_path):
#             for file_path in os.listdir(abs_path):
#                 if file_path.endswith(('png', 'jpg')):
#                     resize_img(os.path.join(abs_path, file_path), size, destination)
#         elif os.path.isfile(abs_path):
#             if abs_path.endswith(('png', 'jpg')):
#                 resize_img(abs_path, size, destination)


if __name__ == '__main__':
    args = parser.parse_args()
    r = ResizeImg(args.source, args.destination, args.size)
    for i in r.yield_source():
        r.resize_img(i)