import os


def capitalize_first(value):
    if not value:
        return value
    return value[0].upper() + value[1:]


def add_pages_root(path, pages_root):
    if not path:
        return path
    path = os.path.join(pages_root, path)
    return path


def add_root(path, root):
    if not path:
        return path
    path = os.path.join(root, path)
    return path


def text_list(lst):
    if not lst:
        return lst
    lst = list(lst)
    if len(lst) == 1:
        return lst[0]
    if len(lst) == 2:
        return  f'{lst[0]} and {lst[1]}'
    return f'{", ".join(lst[:-1])}, and {lst[-1]}'


def code_list(lst):
    return ',\n'.join(lst) + '\n'


def link_list(str2url_dict, pages_root):
    sb = []
    for text, url in str2url_dict.items():
        sb.append(f'<a href="{add_pages_root(url, pages_root)}">{text}</a>')
    return text_list(sb)


def add_html_tabs_newlines(s):
    s = s.replace('\n', '<br>')
    s = s.replace('\t', '&emsp;')
    return s


def replace_tabs_by_spaces(s):
    s = s.replace('\t', '  ')
    return s


def escape_backslashes(s):
    s = s.replace('\\', '\\\\')
    return s