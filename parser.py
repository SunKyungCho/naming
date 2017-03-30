#-*- coding: utf-8 -*-
import fnmatch
import requests
import nltk

import os
import re
# import pandas as pd
# # %matplotlib inline

# java_file = []

def read_source(path):
    try :
        with open(path) as f:
            content = f.read()
        return content
    except :
        return 'file exception'

    return ''


def removeComments(source):
    """
    replacde '/* */' and '//' style comments
    reference : http://blog.ostermiller.org/find-comment
    comment의 열림만 있고 닫힘이 없는 경우 regex에서 hang이 걸리는 경우가 발생함
    이름 방지하기 위해 사용
    """
    source += '*/'

    p = re.compile('(\/\*([^*]|[\r\n]|(\*([^/]|[\r\n])))*\*\/)|(\/\/.*)')
    output = p.sub("", source)

    return output


def cleaning_source(source):
    ## remove ccomments
    source = removeComments(source)

    ## remove "\r"
    source = source.replace("\r","")

    ## split by lines
    source_lines = source.split("\n")

    return source_lines

def parse_source_lines(lines):
    variable_names = []
    variable_set = set()
    for line in lines:
        vals = parseLine(line)
        if  (vals==None):
            continue

        for val in vals :
            ## unique check
            if val[0] not in variable_set:
                variable_names.append(val)
                variable_set.add(val[0])
    return variable_names

##### Variable Extract Rule ###############################

def ev_equal_rule(line):
    """
    변수는 변할수 있는 값이라는 전제로 값을 변하게 하는 equal(=) 연산자의 left token을 변수를 함
    """
    line = line.replace('==',' ')
    equal_pos = line.find('=')
    if equal_pos < 0:
        return None
    line = ''.join( c if (c.isalnum()) | (c=='_') else ' ' for c in line[:equal_pos] )
    val = line.split()[-1]
    if len(val)>0:
        return [val]
    return None

def ev_equal_regex_rule(line):
    """
    '=' 이전에 공백이나 탭이 0~3개 까지 올수 있고
    '=' 이전에 A-Z|a-z|0-9|_ 로 구성된 문자가 오고
    '=' 다음에 '<>!' 문자가 안오는 경우
    """
    regex = r"([A-Za-z0-9\_]+)[ \t]{0,3}\=[^<>!]"
    line += ' '
    matches = re.finditer(regex, line)
    names = []
    for match in matches:
        names.append(match.group(1))
    return names


##### Class Extract Rule ###############################
def ec_prefix_regex_rule(line):
    """
    'class' 단어가 오고
    ' '이 1글자 이상오고
    다음에 a-z, A-Z, _, 0-9 글자로 이루어진 단어를 class명으로 추출
    """
    regex = r"(class) {1,3}([a-zA-Z_0-9]+)"
    line += ' '
    matches = re.finditer(regex, line)
    names = []
    for match in matches:
        names.append(match.group(2))

    return names

def ev_regex_rule(line, regex, groupid):

    line += ' '
    matches = re.finditer(regex, line)

    names = []
    for match in matches:
        names.append(match.group(groupid))
    return names

## 함수명을 추출하는 rule, 단순히 '('가 후미에 있고 단어가 a-z, A-Z, 0-9, _ 구성됨
ef_bracket_regex_rule = lambda line : ev_regex_rule(line, r' {1,3}([a-zA-Z0-9]+) {0,3}\(', 1)

# def ef_braket_regex_rule(line):
#
#     """
#     단순히 '('가 후미에 있고 단어가 a-z, A-Z, 0-9, _ 구성됨
#     """
#     regex = r"{1,3}([a-zA-Z0-9]+) {0,3}\("
#     line += ' '
#     matches = re.finditer(regex, line)
#     names = []
#     for match in matches:
#         names.append(match.group(1))
#     return names


###################################################
def variableValidation(name):
    ## Java 예약어
    reserved_words = set('abstract default package synchronized boolean do if private this break double implements protected throw byte else import public throws switch enum instanceof return try catch extends int short char final interface static void class finally long strictfp volatile float native super while continue for new case goto* null transient const operator future generic ineer outer rest var from'.split())


    name = name.lower()
    ## check reserved words
    if name in reserved_words:
        return False

    ## check start-char is number
    # if name[0].isnumeric():
    if name[0].isdigit():
        return False

    ## check test code's name
    if name.find("test") > -1:
        return False

    return True

def extractVariable(line):
    ## parse rule list
    parse_rules = [
        ('equal:rule', 'variable', ev_equal_regex_rule), ## equal rule by regex
        ('class:rule', 'class', ec_prefix_regex_rule), ##
        ('function:rule', 'function', ef_bracket_regex_rule), ##
    ]

    val_names = []
    for (rule, val_type, parsor) in parse_rules:
        names = parsor(line)
        if (names == None):
            continue
        for name in names:
            val_names.append([name,val_type])

    return val_names

def extractIntent(line):
    intent_char = ' \t'
    pos = 0
    for ch in line:
        if ch not in intent_char:
            break
        pos = pos + (4 if ch == '\t' else 1)
    return pos

def parseLine(line):
    ## check intent
    # don't need intent
    # intent = extractIntent(line)

    ## extract variables
    vals = extractVariable(line)
    if (vals == None) | (len(vals) == 0):
        return None

    ret = []
    for val in vals:

        ## check name validation
        if False==variableValidation(val[0]):
            continue
        ## add char_len vlaue
        val.append(len(val[0]))
        ## add intent value
        # val.append(intent)
        #add tokenizer
        token_variable_list = tokenizer(val[0])
        #소문자 변환
        token_variable_list = lower(token_variable_list)
        token_variable_list_count = len(token_variable_list)
        val.append(token_variable_list);
        val.append(token_variable_list_count);

        ret.append(val)
    return ret

def lower(list):
    result = []
    for word in list:
        result.append(word.lower())
    return result

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
    # if ch.isnumeric(): return 3
    if ch.isdigit(): return 3
    if ch=='_':        return 4
    if ch=='$':        return 0
    return 5

def removeNumber(word):
    removed = ''
    for ch in word:
        # if not ch.isnumeric():
        if not ch.isdigit():
            removed += ch
    return removed


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

def parse_source_code(src_path):

    #소스파일 주석제거
    source = read_source(src_path)
    #파일을 한줄씩 리스트 형태
    source = cleaning_source(source)
    #본격적으로 parsing
    parsed = parse_source_lines(source)

    return parsed

def parse_source_dir(dirname, java_file):
    filenames = os.listdir(dirname)
    for filename in filenames:
        full_filename = os.path.join(dirname, filename)
        if os.path.isdir(full_filename):
            parse_source_dir(full_filename, java_file)
        else:
            ext = os.path.splitext(full_filename)[-1]
            if ext == '.java':
                java_file.append(full_filename)


def parse_project_dir(resource_path):

    project_names = os.listdir(resource_path)

    return project_names

def find_java_file(resource_path, project_name):

    print "parsing : %s ..." % (project_name)
    java_files = []
    project_path = os.path.join(resource_path, project_name)
    parse_source_dir(project_path, java_files)
    print "parsing completed"
    return java_files

def file_write(data_path, project_name, naming_data_list):

    f_path = "%s/%s.csv" % (data_path, project_name)
    f = open(f_path, "a")
    for namingDataSet in naming_data_list:
        for val in namingDataSet:
            f.write("%s," % val)
        f.write(project_name+"\n")
    f.close()

def parse_naming():
    path = os.path.dirname(os.path.realpath(__file__))
    resource_path = os.path.join(path, 'resource')
    data_path = os.path.join(path, 'data')

    project_names = parse_project_dir(resource_path)
    print "project count : %d " % (len(project_names))
    for project_name in project_names:
        if not project_name.startswith('.'):
            java_file_list = find_java_file(resource_path, project_name)
            for file_path in java_file_list:
                naming_data_list = parse_source_code(file_path)
                file_write(data_path, project_name, naming_data_list)
            print "file writing completed %s,  file count = %d" % (project_name, len(java_file_list))


def main():

    print "start"
    parse_naming()



if __name__ == '__main__':
    main()

