import pdfplumber
import re
import sys, getopt
#for line in ls -d PDF/*; do python3 PDFplumb.py $line; done

args = sys.argv
print(args)

filepath = '/home/t/Documents/Accounting/PDF/2020-05-26_Statement.pdf'
outfile = '/home/t/Documents/Accounting/CSV/report.csv'
outCSV=''
filepath=args[1]

stateVar = {
        "currentState" : "outside",
        "currentTransaction": "",
        "CurrentDate": ""
    }

date_re = re.compile(r'^\d{2} [A-Z][a-z]{2} \d{2}.*')
firstline_re = re.compile(r'BALANCEBROUGHTFORWARD')
lastline_re = re.compile(r'BALANCECARRIEDFORWARD')
transtype_re = re.compile(r'VIS|DR|DD|\)\)\)|TRF|SO|CR|CHQ|BACS|ATM')
money_re = re.compile(r'([0-9]{1,3},){0,}[0-9]{1,3}\.[0-9]{2}')


def pushLine(line):
    global outCSV
    print(line)
    outCSV += "\n" + line


def moneyType(word):
    if 380<word['x1'] and (word['x1']<400) and money_re.search(word['text']):
        return "; -{}".format(word["text"])
    if 455<word['x1'] and (word['x1']<475) and money_re.search(word['text']):
        return "; +{}".format(word["text"]) 
    if 535<word['x1'] and (word['x1']<565) and money_re.search(word['text']):
        return "; {}".format(word["text"])     
    return False



def WRMachine(word):
    
    def outside(word):
        
        if firstline_re.search(word["text"]) != None:
            stateVar["currentState"] = "beforeTrans"


    def beforeTrans(word):
        if date_re.search(word["text"]):
            stateVar["currentDate"] = word["text"] + ";"
        if transtype_re.search(word["text"]):
            stateVar["currentTransaction"] += word["text"]+ ";"
            stateVar["currentState"] = "inTrans"
        if lastline_re.search(word["text"]):
            stateVar["currentState"] = "outside"

    def inTrans(word):
        if moneyType(word):
            stateVar["currentTransaction"] += moneyType(word)
            stateVar["currentState"] = "endTrans"
        else:
            stateVar["currentTransaction"] +=" " + word["text"]
        

    def endTrans(word):
        if moneyType(word):
            stateVar["currentTransaction"] += moneyType(word)
        stateVar["currentState"] = "beforeTrans"
        stateVar["currentTransaction"] = stateVar["currentDate"] + " " + stateVar["currentTransaction"]
        pushLine(stateVar["currentTransaction"])
        
        stateVar["currentTransaction"] = ""
        beforeTrans(word)


    
    next = {
        "outside" : outside,
        "beforeTrans" : beforeTrans,
        "inTrans" : inTrans,
        "endTrans": endTrans
    }

    def step(word):
        next[stateVar["currentState"]](word)

    step(word)
        
print(outCSV)

with pdfplumber.open(filepath) as pdf:

    for page in pdf.pages:
        words = page.extract_words(
                x_tolerance=10 , 
                y_tolerance=3, 
                keep_blank_chars=True, 
                use_text_flow=True, 
                horizontal_ltr=True, 
                vertical_ttb=True, 
                extra_attrs=[])
        words.sort(key=lambda x: x['bottom'])

        currentLineBottom = 0
        currentLine = ""
        tableSwitch = False
        currentDate = ""
        currentTransaction = ""
        for word in words:
            txt = word['text']
            WRMachine(word)

with open(outfile,"a") as oCSV:
    oCSV.write(outCSV)