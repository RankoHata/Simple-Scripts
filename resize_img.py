import os
import argparse
from PIL import Image

parser = argparse.ArgumentParser(
    description='Resize Image...'
)

parser.add_argument('-s', '--source', dest='source', nargs='*', help='All Source File Path.')
parser.add_argument('-d', '--destination', dest='destination', action='store', help='Destination directory for new files.')
# parser.add_argument('-x', '--width', dest='width', action='store')
# parser.add_argument('-y', '--height', dest='height', action='store')
parser.add_argument('--size', dest='size', nargs=2)


def get_destination(args):
    destination = os.path.abspath(args.destination)
    print(destination)
    if not os.path.exists(destination):
        os.makedirs(destination)
    if os.path.isdir(destination):
        return destination
    else:
        return None


def resize_img(file_path, size, destination):
    print('resize')
    filename = os.path.basename(file_path)
    img = Image.open(file_path)
    img = img.resize(size, Image.ANTIALIAS)
    img.save(os.path.join(destination, 'size_{}_'.format(size) + filename))


def main(args):
    destination = get_destination(args)
    size = tuple(int(i) for i in args.size)
    if destination is None:
        destination = os.path.abspath(os.curdir)
    for item in args.source:
        print(item)
        abs_path = os.path.abspath(item)
        if os.path.isdir(abs_path):
            for file_path in os.listdir(abs_path):
                if file_path.endswith(('png', 'jpg')):
                    resize_img(os.path.join(abs_path, file_path), size, destination)
        elif os.path.isfile(abs_path):
            if abs_path.endswith(('png', 'jpg')):
                resize_img(abs_path, size, destination)


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
