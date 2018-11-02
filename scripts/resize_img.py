"""Resize Image Files.

Resize Image Files (.png and .jpg).
Change the image size proportionally or at a fixed value.

This is a command line tool.
You can execute the following instructions:
    - example1: python resize_img.py --width 200 --height 400
    - example2: python resize_img.py --width 50% --height 30%
"""

import os
import re
import sys
import logging
import argparse
from PIL import Image

# Types
INTEGER    = 0x01
PERCENTAGE = 0x02

logging.basicConfig(level=logging.DEBUG)

px_re_str = re.compile(r'(\d+)')  # integer
ratio_re_str = re.compile(r'(\d+%)')  # percentage

parser = argparse.ArgumentParser(
    description='Resize Image...'
)

parser.add_argument('-s', '--source', dest='source', nargs='*', help='Path to all source files.')  # 空会返回 None
parser.add_argument('-d', '--destination', dest='destination', action='store', help='Destination directory for new files.')
parser.add_argument('--width', dest='width', action='store', help='eg: 50 or 50%')
parser.add_argument('--height', dest='height', action='store', help='eg: 50 or 50%')
# parser.add_argument('--size', dest='size', action='store', help='width and height')


class SizeTypeError(Exception):
    pass


class TypeSize(object):
    """ Value with type."""
    def __init__(self, value: int, type_: str):
        self.value = value
        self.type = type_


class Size(object):
    def __init__(self, width, width_type, height, height_type):
        self.width = TypeSize(width, width_type)
        self.height = TypeSize(height, height_type)


class ResizeImg(object):
    def __init__(self, source, destination, width: str, height: str):
        """The class that change the size of images.

        source:       [str, ...] or None    Path to the all source files. (directory or file)
        destination:  str                   Destination directory for new files.
        width:        str                   eg: 50 or 50%
        height:       str                   eg: 50 or 50%
        """
        self.source = source if source is not None else [os.curdir]
        self.destination = self.get_destination(destination)
        self.size = self.get_size(width, height)  # eg: ((50, PERCENTAGE), (100, INTEGER))
    
    def yield_source(self):
        """Generate absolute path to all files."""
        for item in self.source:
            abs_path = os.path.abspath(item)
            if os.path.isdir(abs_path):
                for file_path in os.listdir(abs_path):
                    if file_path.endswith(('png', 'jpg')):
                        yield file_path
            elif os.path.isfile(abs_path):
                if abs_path.endswith(('png', 'jpg')):
                    yield abs_path
            else:
                logging.error('Invalid Path: {}'.format(abs_path))

    def resize_img(self):
        """ Resize all image. """
        for file_path in self.yield_source():
            filename = os.path.basename(file_path)
            img = Image.open(file_path)
            raw_width, raw_height = img.size
            
            size_tuple = self.get_size_value(raw_width, raw_height)

            img = img.resize(size_tuple, Image.ANTIALIAS)
            img.save(os.path.join(self.destination, 'size_{}_'.format(size_tuple) + filename))  # 重名会出bug,暂时不改了
            
    def get_size_value(self, raw_width, raw_height) -> tuple:
        """ Calculated actual width and height according to type. """

        if self.size.width.type == PERCENTAGE:
            width = raw_width * self.size.width.value // 100
        elif self.size.width.type == INTEGER:
            width = self.size.width.value
        else:
            raise SizeTypeError

        if self.size.height.type == PERCENTAGE:
            height = raw_height * self.size.height.value // 100
        elif self.size.height.type == INTEGER:
            height = self.size.height.value
        else:
            raise SizeTypeError

        return(width, height)

            


    def get_size(self, width: str, height: str) -> tuple:
        """ Add type. """
        width = self.re_getattr(width)
        height = self.re_getattr(height)
        tmp = []
        for i in (width, height):
            if i[-1] == '%':
                tmp.append(int(i[:-1]))
                tmp.append(PERCENTAGE)
            else:
                tmp.append(int(i))
                tmp.append(INTEGER)
        return Size(*tmp)

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
