# -*- coding: utf-8 -*-

import locale
from yandex import Translater


class YandexTranslator:
    api_key = 'trnsl.1.1.20170617T184728Z.e5610c45350ca667.79c5d1922fb47c91e7ae727d6169aa3d5706669b'  # Api key found on https://translate.yandex.com/developers/keys

    def __init__(self):
        locale.setlocale(locale.LC_ALL, '')

    def translate(self, text, toLang, fromLang=None):
        tr = Translater()
        tr.set_key(self.api_key)
        tr.set_text(text)

        if fromLang is None:
            fromLang = tr.detect_lang()
            if fromLang is None:
                fromLang = 'de'

        tr.set_from_lang(fromLang)
        tr.set_to_lang(toLang)
        return tr.translate()


if __name__ == '__main__':
    yt = YandexTranslator()
    print str(yt.translate('Clock', 'de', 'en'))
