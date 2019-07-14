# JamSpell

[![Build Status][travis-image]][travis] [![Release][release-image]][releases]

[travis-image]: https://travis-ci.org/bakwc/JamSpell.svg?branch=master
[travis]: https://travis-ci.org/bakwc/JamSpell

[release-image]: https://img.shields.io/badge/release-0.0.11-blue.svg?style=flat
[releases]: https://github.com/bakwc/JamSpell/releases

JamSpell is a spell checking library with following features:

- **accurate** - it consider words surroundings (context) for better correction
- **fast** - near 5K words per second
- **multi-language** - it's written in C++ and available for many languages with swig bindings

## Content
- [Benchmarks](#benchmarks)
- [Usage](#usage)
  - [Python](#python)
  - [C++](#c)
  - [Other languages](#other-languages)
  - [HTTP API](#http-api)
- [Train](#train)

## Benchmarks

<table>
  <tr>
    <td></td>
    <td>Errors</td>
    <td>Top 7 Errors</td>
    <td>Fix Rate</td>
    <td>Top 7 Fix Rate</td>
    <td>Broken</td>
    <td>Speed<br>
(words/second)</td>
  </tr>
  <tr>
    <td>JamSpell</td>
    <td>3.25%</td>
    <td>1.27%</td>
    <td>79.53%</td>
    <td>84.10%</td>
    <td>0.64%</td>
    <td>4854</td>
  </tr>
  <tr>
    <td>Norvig</td>
    <td>7.62%</td>
    <td>5.00%</td>
    <td>46.58%</td>
    <td>66.51%</td>
    <td>0.69%</td>
    <td>395</td>
  </tr>
  <tr>
    <td>Hunspell</td>
    <td>13.10%</td>
    <td>10.33%</td>
    <td>47.52%</td>
    <td>68.56%</td>
    <td>7.14%</td>
    <td>163</td>
  </tr>
  <tr>
    <td>Dummy</td>
    <td>13.14%</td>
    <td>13.14%</td>
    <td>0.00%</td>
    <td>0.00%</td>
    <td>0.00%</td>
    <td>-</td>
  </tr>
</table>

Model was trained on [300K wikipedia sentences + 300K news sentences (english)](http://wortschatz.uni-leipzig.de/en/download/). 95% was used for train, 5% was used for evaluation. [Errors model](https://github.com/bakwc/JamSpell/blob/master/evaluate/typo_model.py) was used to generate errored text from the original one. JamSpell corrector was compared with [Norvig's one](http://norvig.com/spell-correct.html), [Hunspell](http://hunspell.github.io/) and a dummy one (no corrections).

We used following metrics:
- **Errors** - percent of words with errors after spell checker processed
- **Top 7 Errors** - percent of words missing in top7 candidated
- **Fix Rate** - percent of errored words fixed by spell checker
- **Top 7 Fix Rate** - percent of errored words fixed by one of top7 candidates
- **Broken** - percent of non-errored words broken by spell checker
- **Speed** - number of words per second

To ensure that our model is not too overfitted for wikipedia+news we checked it on "The Adventures of Sherlock Holmes" text:

<table>
  <tr>
    <td></td>
    <td>Errors</td>
    <td>Top 7 Errors</td>
    <td>Fix Rate</td>
    <td>Top 7 Fix Rate</td>
    <td>Broken</td>
    <td>Speed
(words per second)</td>
  </tr>
  <tr>
    <td>JamSpell</td>
    <td>3.56%</td>
    <td>1.27%</td>
    <td>72.03%</td>
    <td>79.73%</td>
    <td>0.50%</td>
    <td>5524</td>
  </tr>
  <tr>
    <td>Norvig</td>
    <td>7.60%</td>
    <td>5.30%</td>
    <td>35.43%</td>
    <td>56.06%</td>
    <td>0.45%</td>
    <td>647</td>
  </tr>
  <tr>
    <td>Hunspell</td>
    <td>9.36%</td>
    <td>6.44%</td>
    <td>39.61%</td>
    <td>65.77%</td>
    <td>2.95%</td>
    <td>284</td>
  </tr>
  <tr>
    <td>Dummy</td>
    <td>11.16%</td>
    <td>11.16%</td>
    <td>0.00%</td>
    <td>0.00%</td>
    <td>0.00%</td>
    <td>-</td>
  </tr>
</table>

More details about reproducing available in "[Train](#train)" section.

## Usage
### Python
1. Install ```swig3``` (usually it is in your distro package manager)

2. Install ```jamspell```:
```bash
pip install jamspell
```
3. [Download](#download-models) or [train](#train) language model

4. Use it:

```python
import jamspell

corrector = jamspell.TSpellCorrector()
corrector.LoadLangModel('model_en.bin')

corrector.FixFragment('I am the begt spell cherken!')
# u'I am the best spell checker!'

corrector.GetCandidates(['i', 'am', 'the', 'begt', 'spell', 'cherken'], 3)
# (u'best', u'beat', u'belt', u'bet', u'bent', ... )

corrector.GetCandidates(['i', 'am', 'the', 'begt', 'spell', 'cherken'], 5)
# (u'checker', u'chicken', u'checked', u'wherein', u'coherent', ...)
```

### C++
1. Add `jamspell` and `contrib` dirs to your project

2. Use it:

```cpp
#include <jamspell/spell_corrector.hpp>

int main(int argc, const char** argv) {

    NJamSpell::TSpellCorrector corrector;
    corrector.LoadLangModel("model.bin");

    corrector.FixFragment(L"I am the begt spell cherken!");
    // "I am the best spell checker!"

    corrector.GetCandidates({L"i", L"am", L"the", L"begt", L"spell", L"cherken"}, 3);
    // "best", "beat", "belt", "bet", "bent", ... )

    corrector.GetCandidates({L"i", L"am", L"the", L"begt", L"spell", L"cherken"}, 3);
    // "checker", "chicken", "checked", "wherein", "coherent", ... )
    return 0;
}
```

### Other languages
You can generate extensions for other languages using [swig tutorial](http://www.swig.org/tutorial.html). The swig interface file is `jamspell.i`. Pull requests with build scripts are welcome.

## HTTP API

### Option 1 - python (via flask)
* Will run on port 80, open to anyone (not just localhost) by default. 
* Expects the model to be in the same folder as webserver.py and be named ``` medical_model.bin ``` (since this fork is for the medical spell check)
* Gives a few more options than the c++ option. Specifically these params can be sent with the GET or POST api call
  * ```limit``` ... limit number of items per candidate on response from the /candidates endpoint to this i.e. ```/candidates?limit=1&text=blahblah```
  * ```html``` ... if set, will return a human-readable html table instead of json. Works for /fix and /candidates i.e. ```/fix?html=1&text=blahblah ```

```bash 
python webserver.py
 ```


### Option 2 - c++ 
* Install ```cmake```

* Clone and build medSpellCheck (it includes http server):
```bash
git clone https://github.com/jackneil/medSpellCheck.git
cd medSpellCheck
mkdir build
cd build
cmake ..
make
```
on Windows replace the 'make' command with:
```bash
cmake --build . --target ALL_BUILD --config Release
```
* [Download](#download-models) or [train](#train) language model
* Run http server:
```bash
./web_server/web_server en.bin localhost 8080
```
* **GET** Request example:
```bash
$ curl "http://localhost:8080/fix?text=I am the begt spell cherken"
I am the best spell checker
```
* **POST** Request example
```bash
$ curl -d "I am the begt spell cherken" http://localhost:8080/fix
I am the best spell checker
```
* Candidate example
```bash
curl "http://localhost:8080/candidates?text=I am the begt spell cherken"
# or
curl -d "I am the begt spell cherken" http://localhost:8080/candidates
```
```javascript
{
    "results": [
        {
            "candidates": [
                "best",
                "beat",
                "belt",
                "bet",
                "bent",
                "beet",
                "beit"
            ],
            "len": 4,
            "pos_from": 9
        },
        {
            "candidates": [
                "checker",
                "chicken",
                "checked",
                "wherein",
                "coherent",
                "cheered",
                "cherokee"
            ],
            "len": 7,
            "pos_from": 20
        }
    ]
}
```
Here `pos_from` - misspelled word first letter position, `len` - misspelled word len

## Train
To train custom model you need:

1. Install ```cmake```

2. Clone and build medSpellCheck:
```bash
git clone https://github.com/jackneil/medSpellCheck.git
cd medSpellCheck
mkdir build
cd build
cmake ..
make
```
* <b>SPECIAL WINDOWS INSTRUCTIONS</b> for building:
  1) MUST HAVE <b>Visual Studio 2019 Community Edition</b> (or greater) installed as well as <b>Visual Studio 2019 C++ Build Tools</b>!!!
  1) ```cmake ..``` will build a shit .exe unless you've followed ^^^
  1) replace the 'make' command with: (note that the jamspell.exe executable will be located in the /build/main/Release/ folder)<br>
  ```cmake --build . --target ALL_BUILD --config Release```


3. Prepare a utf-8 text file with sentences to train at (eg. [```sherlockholmes.txt```](https://github.com/bakwc/JamSpell/blob/master/test_data/sherlockholmes.txt)) and another file with language alphabet (eg. [```alphabet_en.txt```](https://github.com/bakwc/JamSpell/blob/master/test_data/alphabet_en.txt))

4. Train model:
```bash
./main/jamspell train ../test_data/alphabet_en.txt ../test_data/sherlockholmes.txt model_sherlock.bin
```
5. To evaluate spellchecker you can use ```evaluate/evaluate.py``` script:
```bash
python evaluate/evaluate.py -a alphabet_file.txt -jsp your_model.bin -mx 50000 your_test_data.txt
```
6. You can use ```evaluate/generate_dataset.py``` to generate you train/test data. It supports txt files, [Leipzig Corpora Collection](http://wortschatz.uni-leipzig.de/en/download/) format and fb2 books.

7. Send it stuff like this: 
``` curl "http://localhost:55555/candidates?text=This is a 62 yer old femle with high blod pressur and she has had a lap appendectoy by an aneesthesiologist also she has dibetes mellitus. she takes 50mg of metopfolol per day and an 81mg asprin and  15miligram hydrochlorathiozide plus his mother is a smker and has had a bunch of seezures. they like icee creem and pzza. hx of coranary artery dizease and has had a transeent ishcemic attak" ```

## Download models
Here is our hank.ai medical model pre-trained on a large medical corpus (a few million records):
- [medical_model.zip](https://drive.google.com/a/hank.ai/file/d/1c0Ntr99pdAlcn9zmcF1YJZ7_7Z3OrM22/view?usp=sharing) (180mb)


Here are a few simple models. They trained on 300K news + 300k wikipedia sentences. We strongly recommend to train your own model, at least on a few million sentences to achieve better quality. See [Train](#train) section above.

 - [en.tar.gz](https://github.com/bakwc/JamSpell-models/raw/master/en.tar.gz) (35Mb)
 - [fr.tar.gz](https://github.com/bakwc/JamSpell-models/raw/master/fr.tar.gz) (31Mb)
 - [ru.tar.gz](https://github.com/bakwc/JamSpell-models/raw/master/ru.tar.gz) (38Mb)
