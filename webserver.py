from flask import Flask, request
import jamspell, json
corrector = jamspell.TSpellCorrector()
corrector.LoadLangModel('model_medical.bin')

MSC = Flask(__name__) #medSpellCheck

@MSC.route("/")
def hello():
    return "Welcome to the Medical Spell Checker service, powered by by Hank AI, Inc."

@MSC.route("/fix")
def fix():
    text = request.args.get('text', default = "", type = str)
    if text == "":
        return "No text received. Usage: url/fix?text=texttomedicalspellcheck"
    return corrector.FixFragment(text)

@MSC.route("/candidates")
def candidates():
    text = request.args.get('text', default = "", type = str)
    limit = request.args.get('limit', default = 5, type = int)
    rval = {}
    runningOffset=0
    print(text)
    print(text.split())
    if text == "":
        return "No text received. Usage: url/candidates?text=texttomedicalspellcheck"
    rval['results'] = []
    words = text.split()
    index = text.index
    for i, word in enumerate(words):
        wordOffset = index(word, runningOffset)
        runningOffset = wordOffset + len(word)
        cands = corrector.GetCandidates(words, i)
        if len(cands) == 0: continue
        if cands[0] == word: continue
        candict = {'candidates': cands[:limit],
        'len': len(word),
        'pos_from': wordOffset
        }
        rval['results'].append(candict)
    print(rval)
    return json.dumps(rval,indent=2)



#if __name__ == '__main__':
#    MSC.run(debug=True, host='0.0.0.0', port=80)