#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Advanced Text Replacer module for a KaiSD Text Tools.

(c) 2013 Ivan "Kai SD" Korystin 

License: GPLv3
'''
import re
class ATR:
    '''
    Advanced Text Replacer - is a class, created to make multiple replacements
    in the content or names of text file.
    It can make plain replacements, or use ATG templates to do something more complex.  
    '''

    def __init__(self, files):
        '''
        Constructor
        '''
        self.files = files
        self.replacements = []
    
    def plain_replace(self, pattern, string, regexp=False):
        '''
        Replaces the given pattern with string in files.
        '''
        if regexp:
            pattern = re.compile(pattern)
        self.replacements.append((pattern, string))
    
    
    def templated_replace(self, pattern, template, data, keyFormat='filename', regexp=False):
        '''
        Replaces the given pattern with data formated by template.
        Valid values for keyFormat:
        filename - take data rows by filename(path ignored), key value of the data row should store the filename.
        fullname - as filename, but with path.
        index - take data rows in order, key value of the data row should store the index. Indexes starts with 0.
        If filename or index cannot be found in data keys, pattern will not be replaced. 
        '''
        if regexp:
            pattern = re.compile(pattern)
        strings = template.process(data)
        self.replacements.append((pattern, strings, keyFormat))
            
    
    def write_in_place(self):
        '''
        Do replacement and save the files
        '''
        for f in self.files:
            out = u''
            with open(f, 'rb') as file:
                out = file.read()
            
            idx = 0
            for r in self.replacements:
                if type(r[0]) in (str, unicode):
                    pattern = re.compile(re.escape(r[0]))
                    string = r[1]
                elif type(r[0]) is dict and len(r) == 3:
                    if r[2] == 'filename':
                        fname = f.replace('\\', '/').split('/')[-1]
                        string = f[1].get(fname, None)
                    elif r[2] == 'fullname':
                        string = f[1].get(f, None)
                    elif r[2] == 'index':
                        fname = f.replace('\\', '/').split('/')[-1]
                        string = f[1].get(idx, None)
                    else:
                        raise BaseException('Unknown data key format.')
                elif hasattr(r[0], 'match'):
                    pattern = r[0]
                    string = r[1]
                else:
                    raise BaseException('Unknown pattern type.')
                if string:
                    out = re.sub(pattern, string, out)
                    
            with open(f, 'wb') as outfile:
                outfile.write(out)
    
    def write_new_files(self, outfiles):
        '''
        Do replacement, but save to given files instead of the original ones.
        '''
        if not len(outfiles) == len(self.files):
            raise BaseException('Lists of original and new files has different length.')
        
        for f in self.files:
            out = u''
            with open(f, 'rb') as file:
                out = file.read()
            
            idx = 0
            for r in self.replacements:
                if type(r[0]) in (str, unicode):
                    pattern = re.compile(re.escape(r[0]))
                    string = r[1]
                elif type(r[0]) is dict and len(r) == 3:
                    if r[2] == 'filename':
                        fname = f.replace('\\', '/').split('/')[-1]
                        string = f[1].get(fname, None)
                    elif r[2] == 'fullname':
                        string = f[1].get(f, None)
                    elif r[2] == 'index':
                        fname = f.replace('\\', '/').split('/')[-1]
                        string = f[1].get(idx, None)
                    else:
                        raise BaseException('Unknown data key format.')
                elif hasattr(r[0], 'match'):
                    pattern = r[0]
                    string = r[1]
                else:
                    raise BaseException('Unknown pattern type.')
                if string:
                    out = re.sub(pattern, string, out)
                    
            with open(outfiles[self.files.index(f)], 'wb') as outfile:
                outfile.write(out)
    
    def replace_in_names(self):
        '''
        Do replacement, but in file names instead of file content. Returns the list of new file names,
        you can use it with writeNewFiles() method. 
        '''
        out = []
        for f in self.files:
            new = f
            idx = 0
            for r in self.replacements:
                if type(r[0]) in (str, unicode):
                    pattern = re.compile(re.escape(r[0]))
                    string = r[1]
                elif type(r[0]) is dict and len(r) == 3:
                    if r[2] == 'filename':
                        fname = f.replace('\\', '/').split('/')[-1]
                        string = f[1].get(fname, None)
                    elif r[2] == 'fullname':
                        string = f[1].get(f, None)
                    elif r[2] == 'index':
                        fname = f.replace('\\', '/').split('/')[-1]
                        string = f[1].get(idx, None)
                    else:
                        raise BaseException('Unknown data key format.')
                elif hasattr(r[0], 'match'):
                    pattern = r[0]
                    string = r[1]
                else:
                    raise BaseException('Unknown pattern type.')
                if string:
                    new = re.sub(pattern, string, new)
            out.append(new)
        return out
                    
    def clear_replacements(self):
        '''
        Removes all replacements.
        '''
        self.replacements = []
    
    def log(self, string):
        '''
        Print information
        '''
        pass