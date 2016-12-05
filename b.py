
def charType(ch):
    if ch=='_':
        return 'underbar'
    
    if ch.isnumeric():
        return 'numeric'
    
    if not ch.isalpha():
        return 'unknown'
    
    if ch.islower():
        return 'lower'
    else :
        return 'upper'

    return 'unknown'

def chLevel(ch):
    if ch.islower():   return 1
    if ch.isupper():   return 2
    if ch.isnumeric(): return 3
    if ch=='_':        return 4
    if ch=='$':        return 0
    return 5

def removeNumber(word):
    removed = ''
    for ch in word:
        if not ch.isnumeric():
            removed += ch
    return removed


## https://en.wikipedia.org/wiki/Naming_convention_(programming)#Java 
def tokenizer(sentance):
    """ 
    naming된 sentance를 단어로 tokenizing 한다. 
    java naming convention에 기반하여 check
    UpperCamelCase, lowerCamelCase, lower_delimiter_case, UPPER_DELIMITER_CASE 
    위의 4가지 naming convention 으로 tokenize 실행 
    """
    
    ### inspection split char posision 
    old_level = 0
    split_pos = []
    last_pos = 0
    for pos, ch in enumerate(sentance):
        cur_level = chLevel(ch)
        if (cur_level < old_level) & (pos>1) :  ## lower edge
            if old_level == 3: 
                split_pos.append(last_pos)
            elif (pos - last_pos)<2:
                split_pos.append(last_pos)
            else :
                split_pos.extend([last_pos,pos-1])
            last_pos = pos
        elif ( cur_level > old_level ): ## upper edge
            #print('set')
            last_pos = pos
        old_level = cur_level
        

    ### word split 
    last_pos = 0
    words = []
    split_pos.append(pos+1)
    for pos in split_pos:
        if sentance[last_pos]=='_':
            last_pos += 1
        w = removeNumber(sentance[last_pos:pos])
        if len(w)>0:
            words.append( w )
        last_pos=pos
    return words 


print(tokenizer('parseDBMXMLFromIPAddress'))
testSentance = ['test100', 'tokenStats', 'ActiveMQQueueMarshaller', 
                'parseDBMXMLFromIPAddress', 'TestMapFile', 'TEST_NUMVER_AA', 'my_number']
for word in testSentance:
    print(tokenizer(word))

    for word in testSentance:
    print('^'+word)
    print(''.join(['0']+[ str(chLevel(ch)) for ch in word]))

