from copy import copy
from csv import DictWriter
import os

initialCodeSmellsStatistic = {
    "repetitiveCodeLines" : 0,
    "DeadCodesAfterReturn" : 0,
    "MultipleReturnStatementsInFunction" : 0,
    "LongStatements" : 0,
    "MultipleSameFunctionNames" : 0,
    "LongClassOrMethod": 0,
    "LongLoopBlocks": 0,
    "LongConditionalBlocks": 0,
    "LongParameterList": 0
}
functionNames = None
codeSmellsStatistic = None

def describeCodeSmell(description, start, end, codeSmell):
    print(description, end = " ")
    if (start == end):
        print("at line", start + 1)
    else:
        print("from line", start + 1, "to line", end + 1)
    codeSmellsStatistic[codeSmell] += 1

def getLeadingSpaces(line):
    return len(line) - len(line.lstrip())

def getFunctionName(line):
    functionName = line.split()[1]
    if ('(' in functionName):
        functionName = functionName[:functionName.index('(')]
    return functionName

def hasReturnStatement(line):
    return "return" in line.split()

def checkRepetitiveCode(code):
    combinedMultipleLines = []
    for i in range(len(code) - 2):
        flag = True
        codeLines = ""
        for j in range(i, i + 3):
            if (code[j].lstrip() == ""):
                flag = False
                break
            codeLines += code[j].lstrip()
        if (flag):
            combinedMultipleLines.append({ "codeLines": codeLines, "lineRange": [i + 1, i + 3] })
    newlist = sorted(combinedMultipleLines, key=lambda d: d['codeLines'])
    i = 0
    j = 1
    while(j < len(newlist)):
        if (newlist[j]["codeLines"] == newlist[i]["codeLines"]):
            j += 1
        else:
            if ((i + 1) != j):
                ranges = []
                for k in range(i, j):
                    ranges.append(newlist[k]['lineRange'])
                describeCodeSmell(
                    "Repetative more than 2 lines of code found:\n" + newlist[i]["codeLines"] + " at " + str(ranges),
                    newlist[i]['lineRange'][0],
                    newlist[j - 1]['lineRange'][1],
                    "repetitiveCodeLines"
                )
            i = j
            j = i + 1

def checkDeadcodeAfterReturn(code, i):
    numberOfLines = len(code)
    leadingSpaces = getLeadingSpaces(code[i])

    j = i + 1
    while (j < numberOfLines and leadingSpaces == getLeadingSpaces(code[j])):
        j += 1
    if (i+1 != j):
        describeCodeSmell('Dead Code found after Return Statement', i + 1, j - 1, 'DeadCodesAfterReturn')

def checkFunctionHavingMultipleReturn(code, i):
    numberOfLines = len(code)
    leadingSpaces = getLeadingSpaces(code[i])

    j = i
    returnCounts = []
    while (j < numberOfLines and (leadingSpaces <= getLeadingSpaces(code[j]) or code[j].lstrip() == "")):
        if (hasReturnStatement(code[j])): returnCounts.append(j + 1)
        j += 1
    if (len(returnCounts) > 1):
        describeCodeSmell('Multiple return statements found at lines ' + str(returnCounts) + ' of function', i - 1, j - 1, 'MultipleReturnStatementsInFunction')

def checkLongStatements(code, i):
    if (len(code[i].lstrip().split()) > 20):
        describeCodeSmell('Long statement found', i, i, 'LongStatements')

def checkSameFunctionNames(functionNames, numberOfLines):
    functionNames = sorted(functionNames, key=lambda d: d['functionName'])
    i = 0
    j = 1
    while (j < len(functionNames)):
        if (functionNames[i]['functionName'] != functionNames[j]['functionName']):
            if (i + 1 < j):
                lineNumbers = [func['lineNumber'] for func in functionNames[i : j]]
                describeCodeSmell('Multiple functions with same name: ' + functionNames[i]['functionName'] + ' found at lines '+ str(lineNumbers), 0, numberOfLines - 1, 'MultipleSameFunctionNames')
            i = j
        j += 1
    if (i + 1 < j):
        print(i, j)

def checkLongBlocks(code, i, blockType):
    numberOfLines = len(code)
    leadingSpaces = getLeadingSpaces(code[i])

    j = i
    while (j < numberOfLines and (leadingSpaces <= getLeadingSpaces(code[j]) or code[j].lstrip() == "")):
        j += 1
    if (blockType == "CLASS" and (j - i) > 60):
        describeCodeSmell('Long Class found', i, j - 1, 'LongClassOrMethod')
    if (blockType == "METHOD" and (j - i) > 40):
        describeCodeSmell('Long Method found', i, j - 1, 'LongClassOrMethod')
    if (blockType == "LOOP" and (j - i) > 20):
        describeCodeSmell('Long Loop Blocks found', i, j - 1, 'LongLoopBlocks')
    if (blockType == "CONDITIONAL" and (j - i) > 10):
        describeCodeSmell('Long Conditional Blocks found', i, j - 1, 'LongConditionalBlocks')

def checkLongParameterList(code, i):
    if (len(code[i].split(',')) > 4):
        describeCodeSmell('Long parameter list found', i, i, 'LongParameterList')

def checkBlocks(code, i):
    ifConditions = ["if(", "if "]
    otherConditions = ["else(", "else ", "elif(", "elif ", "case "]
    if (code[i].lstrip()[0 : 4] == "def "):
        functionNames.append({
            'functionName': getFunctionName(code[i]),
            'lineNumber': i + 1,
        })
        checkFunctionHavingMultipleReturn(code, i + 1)
        checkLongParameterList(code, i)
        blockType = "METHOD"
    elif (code[i].lstrip()[0 : 6] == "class "):
        blockType = "CLASS"
    elif (code[i].lstrip()[0 : 3] in ifConditions or code[i].lstrip()[0 : 3] in otherConditions):
        blockType = "CONDITIONAL"
    else:
        blockType = "LOOPS"
    checkLongBlocks(code, i + 1, blockType)

def findCodeSmells(fileName):
    file1 = open(fileName, 'r')
    code = file1.readlines()
    numberOfLines = len(code)
    i = 0
    checkRepetitiveCode(code)
    while (i < numberOfLines):
        if (hasReturnStatement(code[i])):
            checkDeadcodeAfterReturn(code, i)
        if (len(code[i]) > 1 and code[i][-2] == ':'):
            checkBlocks(code, i)
        checkLongStatements(code, i)
        i += 1
    checkSameFunctionNames(functionNames, numberOfLines)

folders = ['./']
pythonFilePaths = []
folderIndex = 0
while (folderIndex < len(folders)):
    folder = folders[folderIndex]
    contents = os.listdir(folder)
    for content in contents:
        contentPath = folder + content
        if (os.path.isfile(contentPath)):
            if (contentPath.endswith(".py") and contentPath != './codeSmellDetection.py'):
                pythonFilePaths.append(contentPath)
        else:
            folders.append(contentPath + '/')
    folderIndex += 1

codeSmellsStatistics = []
for pythonFilePath in pythonFilePaths:
    codeSmellsStatistic = copy(initialCodeSmellsStatistic)
    functionNames = []
    findCodeSmells(pythonFilePath)
    codeSmellsStatistic['file'] = pythonFilePath
    codeSmellsStatistics.append(codeSmellsStatistic)

with open('codeSmellData.csv','w') as outfile:
    writer = DictWriter(outfile, (
        'file',
        'repetitiveCodeLines',
        'DeadCodesAfterReturn',
        'MultipleReturnStatementsInFunction',
        'LongStatements',
        'MultipleSameFunctionNames',
        'LongClassOrMethod',
        'LongLoopBlocks',
        'LongConditionalBlocks',
        'LongParameterList'
    ))
    writer.writeheader()
    writer.writerows(codeSmellsStatistics)