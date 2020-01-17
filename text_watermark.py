import re
import os
from itertools import islice

from crc16pure import crc16xmodem

'''
1.水印字符串编码成二进制
2.二进制数据转为隐写html
3.计算每段话的hash（使用crc16算法），以句号结尾的话是一段话
4.将hash计算成隐写html
5.将html插入每一句的句号前
'''

text = '测试文本，我爱Python。'
water_mark = '懒编程'

class TextWaterMark(object):

    def __init__(self, water_mark):
        self.invisible_html = {
            '00': '&#8234;&#8236;',
            '01': '&#8235;&#8236;',
            '10': '&#8237;&#8236;',
            '11': '&#8238;&#8236;'
        }
        self.breakpoint = '(;´༎ຶД༎ຶ`)'
        self.water_mark = water_mark

    def str_to_binary(self, string: str) -> str:
        binary = '{0:08b}'.format(ord(string), 'b')
        if len(binary) > 8:
            binary = '{0:016b}'.format(ord(string), 'b')
        return binary

    def int_to_binary(self, number: int) -> str:
        binary = '{0:08b}'.format(number, 'b')
        if len(binary) > 8:
            binary = '{0:016b}'.format(number, 'b')
        return binary

    def binary_breakpoint():
        binary = ''.join(self.str_to_binary(x) for x in self.breakpoint)
        return binary[:2]

    def str_to_binary_list(self, string: str) -> list:
        binarys = []
        for s in string:
            binary = self.str_to_binary(s)
            if len(binary) > 8:
                binarys.append(binary[:8])
                binarys.append(binary[8:])
            else:
                binarys.append(binary)
        return binarys

    def binary_to_invisible_html(self, string: list) -> str:
        binarys = self.str_to_binary_list(string)
        invisible_str = ''
        for binary in binarys:
            for i in range(0, len(binary), 2):
                key = binary[i] + binary[i+1]
                result = self.invisible_html[key]
                invisible_str += result
        return invisible_str

    def cut_article(self, content: str) -> list:
        pattern = r'。'
        paragraph_list = re.split(pattern, content)
        return [p for p in paragraph_list if p]

    def hash_paragraph(self, paragraph: str) -> str:
        binary = ''.join(self.str_to_binary(p) for p in paragraph)
        binary = str.encode(binary)
        p_hash = crc16xmodem(binary)
        return self.int_to_binary(p_hash)

    def run(self, path: str):
        if not os.path.exists(path):
            print('Error! {path} file not exsits!')
            return
        content = ''
        with open(path, 'r') as f:
            content = f.read()
        if not content:
            print('Warn! {path} file has not content!')

        invisible_water_mark = self.binary_to_invisible_html(self.water_mark)

        paragraph_list = self.cut_article(content)
        articles = []
        for p in paragraph_list:
            p_hash = self.hash_paragraph(p)
            invisible_str = self.binary_to_invisible_html(p_hash)
            # TODO: 支持英文 . 与中文 。 ，目前很粗暴，直接插 。
            res = p + invisible_str + invisible_water_mark + '。'
            articles.append(res)
        
        article = ''.join(articles)

        dirpath = os.path.dirname(path)
        filefullname = os.path.basename(path)
        splitname = os.path.splitext(filefullname)[-1]
        filename = filefullname.replace(splitname, '')
        final_path = os.path.join(dirpath, f'{filename}_twm{splitname}')
        with open(final_path, 'w') as f:
            f.write(article)

        print('done!')


if __name__ == '__main__':
    wm = TextWaterMark(water_mark)
    wm.run('/Users/ayuliao/Desktop/workspace/PyTextWaterMark/test.txt')
