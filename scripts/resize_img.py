"""
Resize Image Files
"""

import os
import re
import sys
import logging
import argparse
from PIL import Image

INTEGER    = 0x01
PERCENTAGE = 0x02

logging.basicConfig(level=logging.DEBUG)

px_re_str = re.compile(r'(\d+)')
ratio_re_str = re.compile(r'(\d+%)')

parser = argparse.ArgumentParser(
    description=r"""
    Resize Image...
    ---------------------------------------------------------------
    example1: python resize_img.py --width 200 --height 400
    example2: python resize_img.py --width 50% --height 30%
    """
)

parser.add_argument('-s', '--source', dest='source', nargs='*', help='Path to all source files.')  # 空会返回 None
parser.add_argument('-d', '--destination', dest='destination', action='store', help='Destination directory for new files.')
parser.add_argument('--width', dest='width', action='store', help='eg: 50 or 50%')
parser.add_argument('--height', dest='height', action='store', help='eg: 50 or 50%')
# parser.add_argument('--size', dest='size', action='store', help='width and height')


class ResizeImg(object):
    def __init__(self, source, destination, width: str, height: str):
        """
        source:       [str, ...] or None    Path to the all source files. (directory or file)
        destination:  str                   Destination directory for new files.
        width:        str                   eg: 50 or 50%
        height:       str                   eg: 50 or 50%
        """
        self.source = source if source is not None else [os.curdir]
        self.destination = self.get_destination(destination)
        self.size = self.get_size(width, height)  # eg: ((50, PERCENTAGE), (100, INTEGER))
    
    def yield_source(self):
        """ Generate absolute path to all files. """
        for item in self.source:
            abs_path = os.path.abspath(item)
            if os.path.isdir(abs_path):
                for file_path in os.listdir(abs_path):
                    if file_path.endswith(('png', 'jpg')):
                        yield file_path
            elif os.path.isfile(abs_path):
                if abs_path.endswith(('png', 'jpg')):
                    yield abs_path

    def resize_img(self):
        """ Resize all image. """
        flag = (self.size[0][1], self.size[1][1])  # eg: (INTEGER, PERCENTAGE)
        size_ = (self.size[0][0], self.size[1][0])  # eg: (100, 50)
        logging.debug('flag: {}'.format(str(flag)))
        
        for file_path in self.yield_source():
            filename = os.path.basename(file_path)
            img = Image.open(file_path)
            raw_width, raw_height = img.size
            
            size_tuple = self.get_size_value(flag, size_, raw_width, raw_height)

            img = img.resize(size_tuple, Image.ANTIALIAS)
            img.save(os.path.join(self.destination, 'size_{}_'.format(size_tuple) + filename))  # 重名会出bug,暂时不改了
            
    def get_size_value(self, flag, size_, raw_width, raw_height) -> tuple:
        """ Calculated actual width and height according to flag. """
        if flag == (PERCENTAGE, PERCENTAGE):
            width = int(raw_width * size_[0] / 100)
            height = int(raw_height * size_[1] / 100)
        elif flag == (PERCENTAGE, INTEGER):
            width = int(raw_width * size_[0] / 100)
            height = int(size_[1])
        elif flag == (INTEGER, PERCENTAGE):
            width = int(size_[0])
            height = int(raw_height * size_[1] / 100)
        elif flag == (INTEGER, INTEGER):
            width = int(size_[0])
            height = int(size_[1])
        return (width, height)

    def get_size(self, width: str, height: str) -> tuple:
        """ Add flag. """
        width = self.re_getattr(width)
        height = self.re_getattr(height)
        size = []
        for i in (width, height):
            if i[-1] == '%':
                size.append((int(i[:-1]), PERCENTAGE))
            else:
                size.append((int(i), INTEGER))
        return tuple(size)

    @staticmethod
    def re_getattr(str_) -> str:
        """ Extract the value from argument. """
        try:
            item = ratio_re_str.findall(str_)[0]  # 顺序绝对不能错，因为存在包含关系
        except IndexError:
            try:
                item = px_re_str.findall(str_)[0]
            except IndexError:
                logging.error('Arguments Error: {}.'.format(str_))
                sys.exit()
            else:
                return item
        else:
            return item

    @staticmethod
    def get_destination(destination):
        """ Get destination directory. """
        destination = os.path.abspath(destination)  # if destinaton is None, return abspath(curdir).
        if not os.path.exists(destination):
            try:
                os.makedirs(destination)
            except:
                logging.error('Error creating destination directory: {}'.format(destination))
                raise
        return destination


if __name__ == '__main__':
    args = parser.parse_args()
    r = ResizeImg(args.source, args.destination, args.width, args.height)
    r.resize_img()
