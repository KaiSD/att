#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Generates files from csv table.

Part of KaiSD Text Tools

(c) 2013 Ivan "Kai SD" Korystin 

License: GPLv3
'''
from sys import argv
from os.path import split
from att import ATG, CSVData, TemplateV2

if __name__ == '__main__':
    if len(argv) == 3:
        generator = ATG(CSVData(argv[1]), TemplateV2(argv[2]))
        generator.write_files()
    elif len(argv) == 4:
        generator = ATG(CSVData(argv[1]), TemplateV2(argv[2]))
        generator.write_files(argv[3])
    else:
        print 'Usage:', split(argv[0])[-1], '<CSV file>', '<Template file>', '[Output directory]'
        print '(c)2015 Ivan "Kai SD" Korystin' 
