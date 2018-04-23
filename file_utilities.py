
import codecs
from itertools import count


def files_equal(file1, file2):
    """ Compare 2 files by content
    :return: True if files are equal
    """
    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        while True:
            data1 = f1.read(4096)
            data2 = f2.read(4096)
            if data1 != data2:
                return False
            if not (data1 and data2):
                return True


def file_line_count(path):
    with open(path) as f:
        return sum(1 for _ in f)


def file_line_count_alt(path):
    # maybe faster
    count = 0
    with open(path, 'rb') as f:
        count += f.read(4096).count('\n')
    return count


def read_csv(file_path, skip=1, limit=None, sep=';', strip=None, codec=None, filter=None):
    """ Generator that reads lines from a (CSV) file
    :param file_path: string
    :param skip: integer>=0, skip this first lines (usually to skip header)
    :param limit: integer>0, limit the number of lines read from file (defalut is no limit)
    :param sep: string, field separator, will not split if None
    :param codec: string, a standard codec or None
    :param filter: (integer>=0, function(2), value), optionally filters the records from the table,
        requires that a sep is specified.
        e.g. filter=(3, str.startswith, '45') will filter on 4th field starting with '45'
    """
    if filter and not sep:
        raise RuntimeError("You must specify a separator if you want a filter")
    with codecs.getreader(codec)(open(file_path, 'rb')) if codec else open(file_path) as f:
        if filter:
            filter_index, filter_func, filter_value = filter
        for _ in xrange(skip):
            if not f.readline().strip():
                return
        for _ in xrange(limit) if limit else count():
            data = f.readline().strip()
            if not data:
                break
            if sep:
                data = data.split(sep)
            if not filter or filter_func(data[filter_index], filter_value):
                yield [d.strip() for d in data] if strip else data
