#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Data module for a Kai's Text Tools.

(c) 2013 Ivan "Kai SD" Korystin 

License: GPLv3
'''

import csv, codecs

class Data(object):
    '''
    Empty data class. Can be used for a subclassing or procedural data creation.
    '''
    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        self.keys = []
        self.rows = []
    
    def __getitem__(self, pair):
        '''
        Returns a value for given key and row. 
        '''
        key = pair[0]
        row = pair[1]
        
        keys = self.keys
        rows = self.rows
        if key in keys:
            if len(rows) > row:
                return rows[row][keys.index(key)]
            else:
                raise BaseException('Row %i not found in data' % (row))
        else:
            raise BaseException('Named value %s not found in data' % (key))
    
    def __setitem__(self, pair, value):
        '''
        Sets a value for given key and row.  
        '''
        key = pair[0]
        row = pair[1]
        
        keys = self.keys
        rows = self.rows
        if key in keys:
            if len(rows) > row:
                rows[row][keys.index(key)] = value
            else:
                raise BaseException('Row %i not found in data' % (row))
        else:
            raise BaseException('Named value %s not found in data' % (key))
    
    def __str__(self):
        '''
        Returns data as string.
        '''
        return str((self.keys, self.rows))
    
    def __repr__(self):
        return self.__str__()
    
    def has_key(self, key):
        '''
        Returns True if given key exists in data
        '''
        return key in self.keys
    
    def add_rows(self, n=1):
        '''
        Adds some empty rows to the data.
        '''
        keys = self.keys
        rows = self.rows
        
        for n in xrange(0, n):
            row = []
            for k in keys:
                row.append('')
            rows.append(row)
    
    def add_keys(self, *h):
        '''
        Adds new keys to the data.
        '''
        keys = self.keys
        rows = self.rows
        
        for i in h:
            keys.append(i)
        for r in rows:
            for i in h:
                r.append('')
    
    def col_by_key(self, key):
        cols = []
        keys = self.keys
        rows = self.rows
        if key in keys:
            idx = keys.index(key)
            for r in rows:
                cols.append(r[idx])
        else:
            raise BaseException('Named value %s not found in data' % (key))
        return tuple(cols)
    
    def row_by_idx(self, idx):
        return tuple(self.rows[idx])

class CSVData(Data):
    '''
    Class for reading CSV files.
    '''
    class Reader:
        class Recoder:
            def __init__(self, f, encoding):
                self.reader = codecs.getreader(encoding)(f)
        
            def __iter__(self):
                return self
        
            def next(self):
                return self.reader.next().encode("utf-8")
        
        def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
            f = self.Recoder(f, encoding)
            self.reader = csv.reader(f, dialect=dialect, **kwds)
    
        def next(self):
            row = self.reader.next()
            return [unicode(s, "utf-8") for s in row]
    
        def __iter__(self):
            return self
    
    def __init__(self, filename, encoding='utf-8', delimiter=';', quotechar='"', **kwargs):
        csvfile = self.Reader(open(filename), encoding=encoding, delimiter=delimiter, quotechar=quotechar)
        sourceData = []
        sourcekeys = None
        
        if kwargs.get('transpose', False):
            sourcekeys = []
            rowData = []
            for i in csvfile:
                sourcekeys.append(i[0])
                for k in xrange(1, len(i)):
                        sourceData.append([])
                        try:
                            i[k] = int(i[k])
                        except:
                            try:
                                i[k] = float(i[k])
                            except:
                                i[k] = i[k]
                rowData.append(i[1:])
            sourceData = list(map(lambda *x:x, *rowData))
        else:
            for i in csvfile:
                if sourcekeys is None:
                    sourcekeys = i
                else:
                    for k in xrange(0, len(i)):
                            try:
                                i[k] = int(i[k])
                            except:
                                try:
                                    i[k] = float(i[k])
                                except:
                                    i[k] = i[k]
                    sourceData.append(i)
        self.keys = sourcekeys
        self.rows = sourceData