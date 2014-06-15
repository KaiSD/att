#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Template module for a Automatic Text Tools.

(c) 2013 Ivan "Kai SD" Korystin 

License: GPLv3
'''

import re
class Template(object):
    '''
    Empty template class. Generates empty text.
    '''
    def process(self, data):
        '''
        Replace this method in subclasses. 
        '''
        return ''
    
    def warning(self, text):
        '''
        Prints a warning
        '''
        print text
    
    def log(self, text):
        '''
        Print information
        '''
        #print 'Template:', text
        pass
    
class TemplateV2(Template):
    '''
    Class for reading ATGv2 templates.
    
    ATGv2 template file should be a plain text file, starting with the line
    ATGV2
    followed by the info line:
    [$KeyField$Extension$Prefix$Encoding$]
    where
    KeyField - is a name of a data column, that contains an identifier.
    Extension - is the desired extension for the generated files.
    Prefix - is the desired filename prefix for the generated files
    Encoding - is the desired encoding for the generated files.
    The line may also have some optional keywords before the closing bracket:
    oneFile$ - place all generated text into a single file instead of
    generating a file for each table row.
    After the info line, you can put your text.
    You can use following commands to handle the data:
    * [$Name$], where Name is the column header,
    will be replaced with value from the current row.
    * [$ATGLINDEX$] will be replaced with the number of a current row.
    * [$ATGHEADER$Text$] and [$ATGFOOTER$Text$] will place the given text
    at the begining or at the end of the file. You can't use other
    commands in this text.
    * [$ATGLIST$Name$Text$], where Name is a multi-column header
    (i.e. 'Col' will represent 'Col1', 'Col2', 'Col3' etc)
    will repeat the given text for each non-empty value.
    You can use other commands in Text. Also [$Name$] inside the list
    will be replaced with the value for the current row and column.
    * [$ATGLINDEX$] can be used only inside the ATGLIST text,
    will be replaced with the current column index.
    * [$ATGLISTCUT$Name$Text$] - same as ATGLIST, but the last symbol
    will be removed. Useful for removing unnecessary newlines.
    * [$ATGIF$Name$Value$Text$] will be replaced with the given text
    only if the the given column's value is the same as the given one.
    Will be replaced with the empty text otherwise. You can use other
    commands in Text.
    * [$ATGIFNOT$Name$Value$Text$] - same as ATGIF, but the column's value
    should not be equal to the given one.
    * [$ATGGREATER$Name$Value$Text$] - same as ATGIF, but the value should
    be the number and it should be greater then the given one.
    * [$ATGGREATER$Name$Value$Text$] - same as ATGGREATER, but the value
    should be less then the given one.
    * [$ATGREPLACE$Text1$Text2$] - Will replace Text1 with Text2. Replacements
    will be done after all other commands. You can't use regular expressions or
    other commands in the text.
    * [$ATGPREFIX$Text$] - Will add the given text to the filename prefix.
    You can use other commands in text, but do it carefully.
    * [$ATGSKIP$] - Skip the current row. Use only in combination with the
    ATGIF/ATGIFNOT, or you will generate nothing.
    * [$ATGPREV$Name$], where Name is the column header,
    will be replaced with the with the value of the given header from the
    previous row. ATGSKIP will be used for the first row.
    '''

    def __init__(self, filename=None, encoding='utf-8', text=''):
        '''
        Constructor.
        
        filename - name of the ATGv2 template file.
        encoding - encoding of the template file.
        text - text to use if no filename has been provided.
        '''
        if filename:
            with open(filename, 'r') as templateFile:
                topline = templateFile.readline().decode(encoding)
                if not topline.startswith('ATGV2'):
                    raise BaseException('%s is not an ATGv2 template' % (filename))
                
                key = templateFile.readline().decode(encoding)
                if key[:2] == '[$' and key[-3:-1] == '$]':
                    keyInfo = key[2:-2].split('$')
                    if len(keyInfo) < 4:
                        raise BaseException('%s has bad ATGv2 key' % (filename))
                    self.keyField = keyInfo[0]
                    self.extension = keyInfo[1]
                    self.prefix = keyInfo[2]
                    self.encoding = keyInfo[3]
                    if 'oneFile' in keyInfo[4:]:
                        self.oneFile = True
                    else:
                        self.oneFile = False
                    self.text = u''
                else:
                    raise BaseException('%s has bad ATGv2 key' % (filename))
                
                for i in templateFile.readlines():
                    self.text += i.decode(encoding)
        else:
            self.text = text
            
        self.header = u''
        self.footer = u''
        self.replacement = {}
        self._data = None
        self._multiWords = None
        
        def parse(text):
            topParts = []
            matches = {}
            
            openers = re.finditer('\[\$.*?\$', text)
            closers = re.finditer('\$\]', text) 
            ops = []
            try:
                cl = closers.next()
                while not cl is None:
                    try:
                        op = openers.next()
                        if op.start() < cl.start():
                            ops.append(op)
                        else:
                            idx = -1
                            try:
                                while ops[idx].start() > cl.start():
                                    idx -= 1
                            except:
                                raise BaseException('Template parsing error: can not find the opener for '+str(cl.start()))
                            matches[ops[idx]] = cl
                            if len(ops) == 1 or idx == -len(ops):
                                topParts.append(ops[idx])
                            del ops[idx]
                            ops.append(op)
                            try:
                                cl = closers.next()
                            except StopIteration:
                                cl = None
                    except StopIteration:
                        idx = -1
                        try:
                            while ops[idx].start() > cl.start():
                                idx -= 1
                        except:
                            raise BaseException('Template parsing error: can not find the opener for '+str(cl.start()))
                        matches[ops[idx]] = cl
                        if len(ops) == 1 or idx == -len(ops):
                                topParts.append(ops[idx])
                        del ops[idx]
                        try:
                            cl = closers.next()
                        except StopIteration:
                            cl = None
            except StopIteration:
                pass
            parts = []
            for i in topParts:
                startPoint = i.end()
                endPoint = matches[i].start()
                p = (i.group()[2:-1], text[startPoint:endPoint])
                if p[0].startswith('ATG'):
                    parts.insert(0, p)
                else:
                    parts.append(p)
            return parts
        
        partCommands = {}
        
        def plain(index, flow, keytag):
            if not keytag in self._data.keys:
                self.warning('WARNING: keyword not found in table - %s' % (keytag))
                return flow
            return flow.replace('[$%s$]' % (keytag), unicode(self._data[keytag, index]))
        partCommands['_ATGPLAIN'] = plain
        
        def nPlain(index, flow, keytag, number):
            if not keytag+str(number) in self._data.keys:
                self.warning('WARNING: keyword not found in table - %s' % (keytag+str(number)))
                return flow
            return flow.replace('[$%s$]' % (keytag), unicode(self._data[keytag+str(number), index]))
        
        def lIndex(index, flow, keytag, number):
            return flow.replace('[$ATGLINDEX$]', str(number))
        
        def addHeader(index, flow, text):
            if self.header.find(text) < 0:
                self.header += text
            key = '[$ATGHEADER$' + text + '$]'
            return flow.replace(key,'')
        partCommands['ATGHEADER'] = addHeader
        
        def addFooter(index, flow, text):
            if self.footer.find(text) < 0:
                self.footer += text
            key = '[$ATGFOOTER$' + text + '$]'
            return flow.replace(key,'')
        partCommands['ATGFOOTER'] = addFooter
        
        def addList(index, flow, string):
            key = '[$ATGLIST$%s$%s$]' % (string.split('$')[0], string[len(string.split('$')[0])+1:])
            sub = string[len(string.split('$')[0])+1:]
            keyTag = string.split('$')[0]
            subparts = parse(sub)
            myText = u''
            if not keyTag in self._multiWords:
                self.warning('Keytag %s is not multiple!' % (keyTag))
                return flow
            for j in xrange(1, self._multiWords[keyTag]+1):
                subText = sub
                for sp in subparts:
                    if sp[0] in self._multiWords:
                        subText = nPlain(index, subText, sp[0], j)
                    elif sp[0] == 'ATGLINDEX':
                        subText = lIndex(index, subText, sp[0], j)
                    elif sp[0] in partCommands:
                        subText = partCommands[sp[0]](index, subText, sp[1])
                    elif sp[1] == '':
                        subText = plain(index, subText, sp[0])
                    else:
                        self.warning('Warning: unknown command '+sp[0])
                if not self._data[keyTag+str(j), index] == u'':
                    myText += subText
            return flow.replace(key, myText)
        partCommands['ATGLIST'] = addList
        
        def addListCut(index, flow, string):
            key = '[$ATGLISTCUT$%s$%s$]' % (string.split('$')[0], string[len(string.split('$')[0])+1:])
            sub = string[len(string.split('$')[0])+1:]
            keyTag = string.split('$')[0]
            subparts = parse(sub)
            myText = u''
            if not keyTag in self._multiWords:
                self.warning('Keytag %s is not multiple!' % (keyTag))
                return flow
            for j in xrange(1, self._multiWords[keyTag]+1):
                subText = sub
                for sp in subparts:
                    if sp[0] in self._multiWords:
                        subText = nPlain(index, subText, sp[0], j)
                    elif sp[0] == 'ATGLINDEX':
                        subText = lIndex(index, subText, sp[0], j)
                    elif sp[0] in partCommands:
                        subText = partCommands[sp[0]](index, subText, sp[1])
                    elif sp[1] == '':
                        subText = plain(index, subText, sp[0])
                    else:
                        self.warning('Warning: unknown command '+sp[0])
                if not self._data[keyTag+str(j), index] == u'':
                    myText += subText
            return flow.replace(key, myText[:-1])
        partCommands['ATGLISTCUT'] = addListCut
        
        def addIf(index, flow, string):
            key = '[$ATGIF$%s$%s$]' % (string.split('$')[0], string[len(string.split('$')[0])+1:])
            sub = string[len(string.split('$')[0])+len(string.split('$')[1])+2:]
            keyTag = string.split('$')[0]
            targetValue = string.split('$')[1]
            subparts = parse(sub)
            myText = u''
            if self._data[keyTag, 0] == []:
                self.warning('WARNING: keyword not found in table - %s' % (keyTag))
                return flow
            if unicode(self._data[keyTag, index]) == unicode(targetValue):
                subText = sub
                for sp in subparts:
                    if sp[0] in partCommands:
                        subText = partCommands[sp[0]](index, subText, sp[1])
                    elif sp[1] == '':
                        subText = plain(index, subText, sp[0])
                    else:
                        self.warning('Warning: unknown command '+sp[0])
                myText += subText        
            return flow.replace(key, myText)
        partCommands['ATGIF'] = addIf
    
        def addIfNot(index, flow, string):
            key = '[$ATGIFNOT$%s$%s$]' % (string.split('$')[0], string[len(string.split('$')[0])+1:])
            sub = string[len(string.split('$')[0])+len(string.split('$')[1])+2:]
            keyTag = string.split('$')[0]
            targetValue = string.split('$')[1]
            subparts = parse(sub)
            myText = u''
            if self._data[keyTag, 0] == []:
                self.warning('WARNING: keyword not found in table - %s' % (keyTag))
                return flow
            if not unicode(self._data[keyTag, index]) == unicode(targetValue):
                subText = sub
                for sp in subparts:
                    if sp[0] in partCommands:
                        subText = partCommands[sp[0]](index, subText, sp[1])
                    elif sp[1] == '':
                        subText = plain(index, subText, sp[0])
                    else:
                        self.warning('Warning: unknown command '+sp[0])
                myText += subText
            return flow.replace(key, myText)
        partCommands['ATGIFNOT'] = addIfNot
        
        def addGreater(index, flow, string):
            key = '[$ATGGREATER$%s$%s$]' % (string.split('$')[0], string[len(string.split('$')[0])+1:])
            sub = string[len(string.split('$')[0])+len(string.split('$')[1])+2:]
            keyTag = string.split('$')[0]
            targetValue = string.split('$')[1]
            subparts = parse(sub)
            myText = u''
            if self._data[keyTag, 0] == []:
                self.warning('WARNING: keyword not found in table - %s' % (keyTag))
                return flow
            try:
                if float(self._data[keyTag, index]) > float(targetValue):
                    subText = sub
                    for sp in subparts:
                        if sp[0] in partCommands:
                            subText = partCommands[sp[0]](index, subText, sp[1])
                        elif sp[1] == '':
                            subText = plain(index, subText, sp[0])
                        else:
                            self.warning('Warning: unknown command '+sp[0])
                    myText += subText
            except:
                self.warning('ERROR: trying to compare uncomparable values!')
            return flow.replace(key, myText)
        partCommands['ATGGREATER'] = addGreater
        
        def addLess(index, flow, string):
            key = '[$ATGLESS$%s$%s$]' % (string.split('$')[0], string[len(string.split('$')[0])+1:])
            sub = string[len(string.split('$')[0])+len(string.split('$')[1])+2:]
            keyTag = string.split('$')[0]
            targetValue = string.split('$')[1]
            subparts = parse(sub)
            myText = u''
            if self._data[keyTag, 0] == []:
                self.warning('WARNING: keyword not found in table - %s' % (keyTag))
                return flow
            try:
                if float(self._data[keyTag, index]) < float(targetValue):
                    subText = sub
                    for sp in subparts:
                        if sp[0] in partCommands:
                            subText = partCommands[sp[0]](index, subText, sp[1])
                        elif sp[1] == '':
                            subText = plain(index, subText, sp[0])
                        else:
                            self.warning('Warning: unknown command '+sp[0])
                    myText += subText
            except:
                self.warning('ERROR: trying to compare uncomparable values!')
            return flow.replace(key, myText)
        partCommands['ATGLESS'] = addLess
        
        def addReplace(index, flow, string):
            key = '[$ATGREPLACE$%s$%s$]' % (string.split('$')[0], string[len(string.split('$')[0])+1:])
            targetString = string[len(string.split('$')[0])+1:]
            srcString = string.split('$')[0]
            self.replacement[srcString] = targetString
            key = '[$ATGREPLACE$' + string + '$]'
            return flow.replace(key,'')
        partCommands['ATGREPLACE'] = addReplace
        
        def addPrefix(index, flow, string):
            key = '[$ATGPREFIX$%s$%s$]' % (string.split('$')[0], string[len(string.split('$')[0])+1:])
            sub = string
            subparts = parse(sub)
            for sp in subparts:
                if sp[0] in partCommands:
                    sub = partCommands[sp[0]](index, sub, sp[1])
                elif sp[1] == '':
                    sub = plain(index, sub, sp[0])
                else:
                    self.warning('Warning: unknown command '+sp[0])
            self.bonusPrefix += sub
            key = '[$ATGPREFIX$' + string + '$]'
            return flow.replace(key,'')
        partCommands['ATGPREFIX'] = addPrefix
        
        def skip(index, flow, string):
            return u'[$ATGSKIP_DO$]'
        partCommands['ATGSKIP'] = skip
        
        def prev(index, flow, string):
            key = '[$ATGPREV$%s$]' % (string.split('$')[0])
            keytag = string.split('$')[0]
            if self._data[keytag, 0] == []:
                self.warning('WARNING: keyword not found in table - %s' % (keytag))
                return flow
            if index == 0:
                self.log('INFORMATION: Skipping ATGPREV tag for entry with index = 0')
                return u'[$ATGSKIP_DO$]'
            return flow.replace('[$ATGPREV$%s$]' % (keytag), unicode(self._data.col_by_key(keytag)[index-1]))
        partCommands['ATGPREV'] = prev
        
        self.commands = partCommands
        self.parts = parse(self.text)
    
    def process(self, data):
        '''
        Generate text for the given data.
        '''
        self._data = data
        
        multiWords = {}
        numbs = ('1','2','3','4','5','6','7','8','9','0')
        
        for i in data.keys:
            multi = False
            while i[-1] in numbs:
                i = i[:-1]
                multi = True
            if multi:
                if i in multiWords:
                    multiWords[i] += 1
                else:
                    multiWords[i] = 1
        self._multiWords = multiWords
        
        if self.oneFile:
            out = ''
        else:
            out = {} 
        index = 0
        partCommands = self.commands
        for element in data.col_by_key(self.keyField):
            self.bonusPrefix = self.prefix
            text = self.text
            for i in self.parts:
                if i[0] in partCommands:
                    text = partCommands[i[0]](index, text, i[1])
                elif i[1] == u'':
                    text = partCommands['_ATGPLAIN'](index, text, i[0])
                else:
                    self.warning('Warning: unknown command '+i[0])
            for i in self.replacement:
                text = text.replace(i, self.replacement[i])
            self.replacement = {}
            index += 1
            
            if u'[$ATGSKIP_DO$]' in text:
                self.log('ATGSKIP Tag found. Skipping ' + unicode(element) + '.')
            else:
                if self.oneFile:
                    out += text
                else:
                    name = self.bonusPrefix + unicode(element)
                    out[name] = self.header + text + self.footer
                self.log('Created %s' % (element))
        
        if self.oneFile:
            out = self.header + out + self.footer
        
        return out
    
    @staticmethod
    def express(cls, text, **kwargs):
        obj = cls()
        obj.text = text
        obj.keyField = kwargs.get('keyField', 'Index')
        obj.extension = kwargs.get('extension', '')
        obj.prefix = kwargs.get('prefix', '')
        obj.encoding = kwargs.get('encoding', 'utf-8')
        return obj