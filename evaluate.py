#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import codecs
import random
import argparse
import typo_model
import time

try:
    import readline
except:
    pass

FNAME = 'sherlockholmes.txt'

class STATE:
    NONE = 0
    LETTER = 1
    DOT = 2
    SPACE = 3

def normalize(text):
    letters = []
    for l in text.lower():
        if l in typo_model.ALPHABET:
            letters.append(l)
        else:
            letters.append(' ')
    text = ''.join(letters)
    text = ' '.join(text.split())
    return text

assert normalize('AsD?! d!@$%^^ ee   ') == 'asd d ee'

def loadText(fname):
    with codecs.open(fname, 'r', 'utf-8') as f:
        data = f.read()
        return normalize(data).split()

def generateTypos(text):
    return map(typo_model.generateTypo, text)

class Corrector(object):
    def __init__(self):
        pass

    def correct(self, sentence, position):
        pass

class DummyCorrector(Corrector):
    def __init__(self):
        super(DummyCorrector, self).__init__()

    def correct(self, sentence, position):
        return sentence[position]

class HunspellCorrector(Corrector):
    def __init__(self, modelPath):
        super(HunspellCorrector, self).__init__()
        import hunspell
        self.__model = hunspell.HunSpell(modelPath + '.dic', modelPath + '.aff')

    def correct(self, sentence, position):
        word = sentence[position]
        if self.__model.spell(word):
            return word
        return self.__model.suggest(word)[0]

class NorvigCorrector(Corrector):
    def __init__(self, trainFile):
        super(NorvigCorrector, self).__init__()
        import norvig_spell
        norvig_spell.init(trainFile)

    def correct(self, sentence, position):
        word = sentence[position]
        import norvig_spell
        return norvig_spell.correction(word)

class ContextCorrector(Corrector):
    def __init__(self, modelPath):
        super(ContextCorrector, self).__init__()
        import context_spell
        context_spell.init(modelPath + '.txt', modelPath + '.arpa')

    def correct(self, sentence, position):
        import context_spell
        return context_spell.correction(sentence, position)

def evaluateCorrector(corrector, originalText, erroredText):
    assert len(originalText) == len(erroredText)
    totalErrors = 0
    lastTime = time.time()
    for pos in xrange(len(originalText)):
        erroredWord = erroredText[pos]
        originalWord = originalText[pos]
        fixedWord = corrector.correct(erroredText, pos)
        if fixedWord != originalWord:
            totalErrors += 1
        if pos % 50 == 0 and pos and time.time() - lastTime > 4.0:
            print '[debug] processed %.2f%%, error rate: %.2f%%' % (100.0 * pos / len(originalText), 100.0 * totalErrors / pos)
            lastTime = time.time()

    return float(totalErrors) / len(originalText)

def testMode(corrector):
    while True:
        sentence = raw_input(">> ").lower().strip()
        sentence = normalize(sentence).split()
        if not sentence:
            continue
        newSentence = []
        for i in xrange(len(sentence)):
            newSentence.append(corrector.correct(sentence, i))
        print ' '.join(newSentence)


def main():
    parser = argparse.ArgumentParser(description='spelling correctors evaluation')
    parser.add_argument('file', type=str, help='text file to use for evaluation')
    parser.add_argument('-hs', '--hunspell' , type=str, help='path to hunspell model')
    parser.add_argument('-ns', '--norvig', type=str, help='path to train file for Norvig spell corrector')
    parser.add_argument('-cs', '--context', type=str, help='path to context spell model')
    parser.add_argument('-t', '--test', action="store_true")
    args = parser.parse_args()

    correctors = {
        'dummy': DummyCorrector(),
    }
    corrector = correctors['dummy']

    if args.hunspell:
        corrector = correctors['hunspell'] = HunspellCorrector(args.hunspell)

    if args.norvig:
        corrector = correctors['norvig'] = NorvigCorrector(args.norvig)

    if args.context:
        corrector = correctors['context'] = ContextCorrector(args.context)

    if args.test:
        return testMode(corrector)

    random.seed(42)
    print '[info] loading text'
    originalText = loadText(args.file)

    print '[info] generating typos'
    erroredText = generateTypos(originalText)

    print '[info] total words: %d' % len(originalText)
    print '[info] evaluating'

    for correctorName, corrector in correctors.iteritems():
        errorsRate = evaluateCorrector(corrector, originalText, erroredText)
        print '[info] "%s": %.2f%%' % (correctorName, 100.0 * errorsRate)


if __name__ == '__main__':
    main()