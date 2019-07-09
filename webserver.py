from flask import Flask, request
from OpenSSL import SSL
import jamspell, json, re
from json2html import *

corrector = jamspell.TSpellCorrector()
corrector.LoadLangModel('model_medical.bin')

MSC = Flask(__name__) #medSpellCheck

formcode = "<form name='checkme' method='get' action=''\n" + \
    "Enter some medical text:<br><textarea id='text' name='text' rows='10' cols='60'></textarea>\n" + \
    "<br><br>Limit: <input id='limit' name='limit' type='number' min='1' max='10' value='2' /> <- only applies if 'candidates' selected\n" + \
    "<br><br>Return type: <select name='route' id='route'><option value='fix'>Fix</option><option value='candidates'>Candidates</option></select>\n" + \
    "<br><br><input type='hidden' name='html' value='1'/><input type='submit' value='Correct It!' /></form>\n\n"

@MSC.route("/")
def hello():
    route = request.args.get('route', default="", type=str)
    if route == 'candidates': return candidates()
    elif route == 'fix': return fix()
    
    #else
    return "<html><head><title>Charting.ai - Medical Spell Check - Powered by Hank Ai, Inc.</title></head>\n" + \
        "<body>Welcome to Medical Spell Check As-A-Service, " + \
        " powered by <a href='https://hank.ai'>Hank AI, Inc.</a><br><br>" + \
    "For API use my endpoints are: <br>1) charting.ai/fix?html=0&text=i am a medical recrd yes i am. i have dibetes and rumatoid arthritis" + \
    "<br>2) charting.ai/candidates?html=0&limit=2&text=i am a medical recrd yes i am. i have dibetes and rumatoid arthritis<br><br><br>" + \
    "Or try me out:<br><br>" + formcode

@MSC.route("/fix")
def fix():
    text = request.args.get('text', default = "", type = str)
    htmlflag = request.args.get('html', default=0, type = int)

    if text == "":
        return "No text received. Usage: url/fix?html=0&text=texttomedicalspellcheck"
    rval = {}
    rval['input']= text
    rval['results'] = corrector.FixFragment(text)
    if text == rval['results']: rval['results']='CORRECT'
    print(htmlflag)
    if bool(htmlflag): return json2html.convert(json.dumps(rval)) + "<br><br><br>Try me out: <br><br>" + formcode
    else: return json.dumps(rval)

@MSC.route("/candidates")
def candidates():
    text = request.args.get('text', default = "", type = str)
    limit = request.args.get('limit', default = 5, type = int)
    htmlflag = request.args.get('html', default=0, type = int)  

    rval = {}
    rval['input'] = text
    runningOffset=0
    if text == "":
        return "No text received. Usage: url/candidates?html=0&limit=2&text=texttomedicalspellcheck"
    rval['results'] = []
    words = re.compile('\w+').findall(text) #text.split()
    index = text.index
    for i, word in enumerate(words):
        wordOffset = index(word, runningOffset)
        runningOffset = wordOffset + len(word)
        cands = corrector.GetCandidates(words, i)
        if len(cands) == 0: continue
        #if word.lower() in [x.lower() for x in cands[:2]]: continue
        if word.lower() == cands[0].lower(): continue
        candict = {'candidates': cands[:limit],
        'len': len(word),
        'pos_from': wordOffset
        }
        rval['results'].append(candict)
    print(rval)
    if len(rval['results'])==0: rval['results']='CORRECT'
    if bool(htmlflag): return json2html.convert(json.dumps(rval)) + "<br><br><br>Try me out: <br><br>" + formcode
    else: return json.dumps(rval,indent=2)



if __name__ == '__main__':
    MSC.run(debug=False, host='0.0.0.0', port=80)