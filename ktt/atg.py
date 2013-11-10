#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Advanced Text Generator module for a KaiSD Text Tools.

(c) 2013 Ivan "Kai SD" Korystin 

License: GPLv3
'''
from os.path import join, exists
from os import makedirs

class ATG(object):
    '''
    Advanced Text Generator is a class, created to generate multiple
    text files from table data.
    '''
    def __init__(self, data, template):
        '''
        Constructor.
        data - an instance of the data.Data class (i.e. CSVData)
        template - an instance of the template.Template class (i.e. TemplateV2)
        '''
        self.data = data
        self.template = template
        self.out = template.process(data)
        
        if type(self.out) == dict:
            self.multiple = True
        else:
            self.multiple = False
    
    def write_files(self, outputDir='.'):
        '''
        Write generated files to the given directory. 
        '''
        encoding = self.template.encoding
        extension = self.template.extension
        out = self.out
        if self.multiple:
            for name in out.keys():
                namepath = name.replace('\\', '/').split('/')
                newpath = u''
                for i in namepath[:-1]:
                    newpath = join(newpath, i)
                if not exists(join(unicode(outputDir),newpath)):
                    makedirs(join(unicode(outputDir),newpath))
                fname = join(unicode(outputDir),name+'.'+extension)
                if fname.endswith('.'):
                    fname = fname[:-1]
                f = open(fname, 'w')
                f.write(out[name].encode(encoding))
                self.log('   Saved %s' % (name+'.'+extension))
                f.close()
        else:
            name = self.template.bonusPrefix
            if name == '.':
                name = self.template.keyField
            namepath = name.replace('\\', '/').split('/')
            newpath = u''
            for i in namepath[:-1]:
                newpath = join(newpath, i)
            if not exists(join(unicode(outputDir),newpath)):
                makedirs(join(unicode(outputDir),newpath))
            f = open(join(unicode(outputDir),name+'.'+extension), 'w')
            f.write(out.encode(encoding))
            self.log('   Saved %s' % (name+'.'+extension))
            f.close()
    
    def log(self, text):
        '''
        Print information
        '''
        #print 'ATG:', text
        pass