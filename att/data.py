#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Data module for a Automatic Text Tools.

(c) 2013 Ivan "Kai SD" Korystin 

License: GPLv3
'''

import csv, codecs, cStringIO

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
    
    def del_row(self, idx):
        '''
        Removes giver row from data
        '''
        del self.rows[idx]
    
    def col_by_key(self, key):
        '''
        Returns a column by header's name
        '''
        keys = self.keys
        if key in keys:
            idx = keys.index(key)
            return self.col_by_idx(idx)
        else:
            raise BaseException('Named value %s not found in data' % (key))
    
    def col_by_idx(self, idx):
        '''
        Returns a column by header's index
        '''
        cols = []
        rows = self.rows
        for r in rows:
            if len(r) > idx:
                cols.append(r[idx])
        return tuple(cols)
    
    def row_by_idx(self, idx):
        '''
        Returns a row by index.
        '''
        return tuple(self.rows[idx])
    
    def transpose(self, key_idx = 0):
        '''
        Returns the transposed copy of the data.
        
        key_idx - index of the column, that contains keywords (default: 0)
        '''
        new_keys = [self.keys[key_idx]]
        new_keys += list(self.col_by_idx(key_idx))
        new_data = Data()
        new_data.keys = new_keys
        
        idx = 0
        for k in self.keys:
            if not idx == key_idx:
                new_row = [k]
                new_row += self.col_by_idx(idx)
                new_data.rows.append(new_row)
            idx += 1
        
        return new_data
    
    def add_data(self, other):
        '''
        Adds rows from another data table to this one.
        '''
        sk = self.keys
        ok = other.keys
        
        for k in ok:
            if not k in sk:
                self.add_keys(k)
        
        for r in  other.rows:
            new_row = []
            if len(r) >= len(sk):
                for k in sk:
                    if k in ok:
                        new_row.append(r[ok.index(k)])
                    else:
                        new_row.append('')
            self.rows.append(new_row)

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
        
        def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwargs):
            f = self.Recoder(f, encoding)
            self.reader = csv.reader(f, dialect=dialect, **kwargs)
    
        def next(self):
            row = self.reader.next()
            return [unicode(s, "utf-8") for s in row]
    
        def __iter__(self):
            return self
    
    class Writer:
        def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwargs):
            self.queue = cStringIO.StringIO()
            self.writer = csv.writer(self.queue, dialect=dialect, **kwargs)
            self.stream = f
            self.encoder = codecs.getincrementalencoder(encoding)()
    
        def writerow(self, row):
            self.writer.writerow([unicode(s).encode("utf-8") for s in row])
            data = self.queue.getvalue()
            data = data.decode("utf-8")
            data = self.encoder.encode(data)
            self.stream.write(data)
            self.queue.truncate(0)
    
        def writerows(self, rows):
            for row in rows:
                self.writerow(row)
    
    def __init__(self, file, encoding='utf-8', delimiter=',', quotechar='"', **kwargs):
        '''
        Constructor.
        
        filename - CSV table filename
        encoding - CSV table encoding (default: utf-8)
        delimiter - CSV table delimiter (default: ;)
        quotechar - CSV table quotechar (default: ")
        '''
        f = None
        if file:
            if type(file) == str:
                f = open(file)
                csvfile = self.Reader(f, encoding=encoding, delimiter=delimiter, quotechar=quotechar)
            else:
                csvfile = self.Reader(file, encoding=encoding, delimiter=delimiter, quotechar=quotechar)

            source_data = []
            source_keys = None;
            
            for i in csvfile:
                if not source_keys:
                    source_keys = i
                else:
                    for k in xrange(0, len(i)):
                        try:
                            i[k] = int(i[k])
                        except:
                            try:
                                i[k] = float(i[k])
                            except:
                                i[k] = i[k]
                    source_data.append(i)
            
            self.keys = source_keys
            self.rows = source_data
            if not f is None:
                f.close();
        else:
            super(CSVData, self).__init__()
    
    def export_csv(self, filename, encoding='utf-8', delimiter=';', quotechar='"', **kwargs):
        '''
        Saves the data to CSV file
        
        filename - CSV table filename
        encoding - CSV table encoding (default: utf-8)
        delimiter - CSV table delimiter (default: ;)
        quotechar - CSV table quotechar (default: ")
        '''
        with open(filename, 'wb') as f:
            csvfile = self.Writer(f, encoding='utf-8', delimiter=';', quotechar='"', **kwargs)
            csvfile.writerow(self.keys)
            csvfile.writerows(self.rows)
