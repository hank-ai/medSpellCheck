from flask import Flask, request
import jamspell, json
from json2html import *

corrector = jamspell.TSpellCorrector()
corrector.LoadLangModel('model_medical.bin')

MSC = Flask(__name__) #medSpellCheck

@MSC.route("/")
def hello():
    return "Welcome to Medical Spell Check As-A-Service, " + \
        " powered by <a href='https://hank.ai'>Hank AI, Inc.</a><br><br>" + \
    "My endpoints: <br>1) charting.ai/fix?html=false&text=text to spellcheck" + \
    "<br>2) charting.ai/candidates?html=false&limit=2&text=text to spellcheck"

@MSC.route("/fix")
def fix():
    text = request.args.get('text', default = "", type = str)
    htmlflag = request.args.get('html', default=False, type = bool)

    if text == "":
        return "No text received. Usage: url/fix?html=0&text=texttomedicalspellcheck"
    rval = {}
    rval['input']= text
    rval['results'] = corrector.FixFragment(text)
    if htmlflag: return json2html.convert(json.dumps(rval))
    else: return json.dumps(rval)

@MSC.route("/candidates")
def candidates():
    text = request.args.get('text', default = "", type = str)
    limit = request.args.get('limit', default = 5, type = int)
    htmlflag = request.args.get('html', default=False, type = bool)  

    rval = {}
    rval['input'] = text
    runningOffset=0
    print(text)
    print(text.split())
    if text == "":
        return "No text received. Usage: url/candidates?html=0&limit=2&text=texttomedicalspellcheck"
    rval['results'] = []
    words = text.split()
    index = text.index
    for i, word in enumerate(words):
        wordOffset = index(word, runningOffset)
        runningOffset = wordOffset + len(word)
        cands = corrector.GetCandidates(words, i)
        if len(cands) == 0: continue
        if cands[0].lower() == word.lower(): continue
        candict = {'candidates': cands[:limit],
        'len': len(word),
        'pos_from': wordOffset
        }
        rval['results'].append(candict)
    print(rval)
    if htmlflag: return json2html.convert(json.dumps(rval))
    else: json.dumps(rval,indent=2)



if __name__ == '__main__':
    MSC.run(debug=True, host='0.0.0.0', port=80)