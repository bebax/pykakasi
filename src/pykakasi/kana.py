# -*- coding: utf-8 -*-
# kana.py
#
# Copyright 2011-2019 Hiroshi Miura <miurahr@linux.com>
#
# Original copyright:
# * KAKASI (Kanji Kana Simple inversion program)
# * $Id: jj2.c,v 1.7 2001-04-12 05:57:34 rug Exp $
# * Copyright (C) 1992
# * Hironobu Takahashi (takahasi@tiny.or.jp)
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either versions 2, or (at your option)
# * any later version.
# *
# * This program is distributed in the hope that it will be useful
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with KAKASI, see the file COPYING.  If not, write to the Free
# * Software Foundation Inc., 59 Temple Place - Suite 330, Boston, MA
# * 02111-1307, USA.
# */

from klepto.archives import file_archive
from pkg_resources import resource_filename
from six import unichr
from six.moves import xrange

from .exceptions import UnsupportedRomanRulesException
from .properties import Configurations


class H2 (object):

    _kanadict = None

    _diff = 0x30a1 - 0x3041  # KATAKANA LETTER A - HIRAGANA A

    def __init__(self, mode, method="Hepburn"):
        if mode == "a":
            if method == "Hepburn":
                self._kanadict = jisyo(Configurations.jisyo_hepburn_hira)
            elif method == "Passport":
                self._kanadict = jisyo(Configurations.jisyo_passport_hira)
            elif method == "Kunrei":
                self._kanadict = jisyo(Configurations.jisyo_kunrei_hira)
            else:
                raise UnsupportedRomanRulesException("Unsupported roman rule")

            self.convert = self.convert_a
        elif mode == "K":
            self.convert = self.convert_K
        else:
            self.convert = self.convert_noop

    def isRegion(self, char):
        return (0x3040 < ord(char[0]) and ord(char[0]) < 0x3097)

    def convert_a(self, text):
        Hstr = ""
        max_len = -1
        r = min(4, len(text) + 1)
        for x in xrange(r):
            if self._kanadict.haskey(text[:x]):
                if max_len < x:
                    max_len = x
                    Hstr = self._kanadict.lookup(text[:x])
        return (Hstr, max_len)

    def convert_K(self, text):
        Hstr = ""
        max_len = 0
        r = len(text)
        for x in xrange(r):
            if self.isRegion(text[x]):
                Hstr = Hstr + unichr(ord(text[x]) + self._diff)
                max_len = max_len + 1
            else:
                break
        return (Hstr, max_len)

    def convert_noop(self, text):
        return (text[0], 1)


class K2 (object):

    _kanadict = None

    _diff = 0x30a1 - 0x3041  # KATAKANA LETTER A - HIRAGANA A

    def __init__(self, mode, method="Hepburn"):
        if mode == "a":
            if method == "Hepburn":
                self._kanadict = jisyo(Configurations.jisyo_hepburn)
            elif method == "Passport":
                self._kanadict = jisyo(Configurations.jisyo_passport)
            elif method == "Kunrei":
                self._kanadict = jisyo(Configurations.jisyo_kunrei)
            else:
                raise UnsupportedRomanRulesException("Unsupported roman rule")  # pragma: no cover

            self.convert = self.convert_a
        elif mode == "H":
            self.convert = self.convert_H
        else:
            self.convert = self.convert_noop

    def isRegion(self, char):
        return 0x30a0 < ord(char[0]) < 0x30fd

    def convert_a(self, text):
        Hstr = ""
        max_len = -1
        r = min(self._kanadict.maxkeylen(), len(text))
        for x in range(1, r + 1):
            if self._kanadict.haskey(text[:x]):
                if max_len < x:
                    max_len = x
                    Hstr = self._kanadict.lookup(text[:x])
            else:  # pragma: no cover
                break
        return Hstr, max_len

    def convert_H(self, text):
        Hstr = ""
        max_len = 0
        r = len(text)
        for x in range(r):
            if self.isRegion(text[x]) and ord(text[x]) < 0x30f7:
                Hstr = Hstr + unichr(ord(text[x]) - self._diff)
                max_len = max_len + 1
            elif self.isRegion(text[x]):
                Hstr = Hstr + text[x]
                max_len = max_len + 1
            else:  # pragma: no cover
                break
        return (Hstr, max_len)

    def convert_noop(self, text):
        return text[0], 1


class jisyo (object):
    _dict = None

    def __init__(self, dictname):
        self._dict = file_archive(resource_filename(__name__, dictname), {}, serialized=True)
        self._dict.load()

    def haskey(self, key):
        return key in self._dict

    def lookup(self, key):
        return self._dict[key]

    def maxkeylen(self):
        return self._dict['_max_key_len_']