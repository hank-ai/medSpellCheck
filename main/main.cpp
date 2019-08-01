#include <iostream>

#include <jamspell/lang_model.hpp>
#include <jamspell/spell_corrector.hpp>
#include "contrib/nlohmann/json.hpp"
#include <cwctype>

using namespace NJamSpell;

void PrintUsage(const char** argv) {
    std::cerr << "Usage: " << argv[0] << " mode args" << std::endl;
    std::cerr << "    train alphabet.txt dataset.txt resultModel.bin  - train model" << std::endl;
    std::cerr << "    score model.bin - input sentences and get score" << std::endl;
    std::cerr << "    scoredcands model.bin - input sentences and get scored candidates" << std::endl;
    std::cerr << "    correct model.bin - input sentences and get corrected one" << std::endl;
    std::cerr << "    fix model.bin input.txt output.txt - automatically fix txt file" << std::endl;
}

int Train(const std::string& alphabetFile,
          const std::string& datasetFile,
          const std::string& resultModelFile)
{
    TLangModel model;
    model.Train(datasetFile, alphabetFile);
    model.Dump(resultModelFile);
    return 0;
}

int Score(const std::string& modelFile) {
    TLangModel model;
    std::cerr << "[info] loading model" << std::endl;
    if (!model.Load(modelFile)) {
        std::cerr << "[error] failed to load model" << std::endl;
        return 42;
    }
    std::cerr << "[info] loaded" << std::endl;
    std::cerr << ">> ";
    for (std::string line; std::getline(std::cin, line);) {
        std::wstring wtext = UTF8ToWide(line);
        std::cerr << model.Score(wtext) << "\n";
        std::cerr << ">> ";
    }
    return 0;
}

int ScoredCands(const std::string& modelFile) {
    TSpellCorrector corrector;
    //std::cerr << "[info] loading model" << std::endl;
    if (!corrector.LoadLangModel(modelFile)) {
        std::cerr << "[error] failed to load model" << std::endl;
        return 42;
    }
    std::cerr << "[info] loaded" << std::endl;
    std::cerr << ">> ";

    for (std::string line; std::getline(std::cin, line);) {
        std::wstring input = UTF8ToWide(line);
        std::transform(input.begin(), input.end(), input.begin(), std::towlower);
        NJamSpell::TSentences sentences = corrector.GetLangModel().Tokenize(input);
        nlohmann::json results;
        results["results"] = nlohmann::json::array();
        //std::cerr << "sentence count = " << sentences.size() << std::endl;
        for (size_t i = 0; i < sentences.size(); ++i) {
            const NJamSpell::TWords& sentence = sentences[i];
            //std::cerr << "sentence " << i << " length = " << sentence.size() << std::endl;
            for (size_t j = 0; j < sentence.size(); ++j) {
                NJamSpell::TWord currWord = sentence[j];
                std::wstring wCurrWord(currWord.Ptr, currWord.Len);
                //std::cerr << "  word " << NJamSpell::WideToUTF8(wCurrWord) << std::endl;
                NJamSpell::TScoredWords candidates = corrector.GetCandidatesScoredRaw(sentence, j);
                if (candidates.empty()) {
                    continue;
                }
                std::wstring firstCandidate(candidates[0].Word.Ptr, candidates[0].Word.Len);
                if (wCurrWord == firstCandidate) { //i.e. the input word was correctly spelled
                    continue;
                }
                nlohmann::json currentResult;
                currentResult["pos_from"] = currWord.Ptr - &input[0];
                currentResult["len"] = currWord.Len;
                currentResult["candidates"] = nlohmann::json::array();
                currentResult["original"] = NJamSpell::WideToUTF8(wCurrWord);

                size_t candidatesSize = std::min(candidates.size(), size_t(7));
                for (size_t k = 0; k < candidatesSize; ++k) {
                    nlohmann::json cand;
                    NJamSpell::TScoredWord candidate = candidates[k];
                    std::string candidateStr = NJamSpell::WideToUTF8(std::wstring(candidate.Word.Ptr, candidate.Word.Len));
                    cand["candidate"] = candidateStr;
                    cand["score"] = candidate.Score;
                    currentResult["candidates"].push_back(cand);
                }

                results["results"].push_back(currentResult);
            }
        }

        std::cerr << results.dump(4) << "\n";
        std::cerr << ">> ";
    }
    return 0;
}

int Fix(const std::string& modelFile,
        const std::string& inputFile,
        const std::string& outFile)
{
    TSpellCorrector corrector;
    std::cerr << "[info] loading model" << std::endl;
    if (!corrector.LoadLangModel(modelFile)) {
        std::cerr << "[error] failed to load model" << std::endl;
        return 42;
    }
    std::cerr << "[info] loaded" << std::endl;
    std::wstring text = UTF8ToWide(LoadFile(inputFile));
    uint64_t startTime = GetCurrentTimeMs();
    std::wstring result = corrector.FixFragment(text);
    uint64_t finishTime = GetCurrentTimeMs();
    SaveFile(outFile, WideToUTF8(result));
    std::cerr << "[info] process time: " << finishTime - startTime << "ms" << std::endl;
    return 0;
}

int Correct(const std::string& modelFile) {
    TSpellCorrector corrector;
    std::cerr << "[info] loading model" << std::endl;
    if (!corrector.LoadLangModel(modelFile)) {
        std::cerr << "[error] failed to load model" << std::endl;
        return 42;
    }
    std::cerr << "[info] loaded" << std::endl;
    std::cerr << ">> ";
    for (std::string line; std::getline(std::cin, line);) {
        std::wstring wtext = UTF8ToWide(line);
        std::wstring result = corrector.FixFragment(wtext);
        std::cerr << WideToUTF8(result) << "\n";
        std::cerr << ">> ";
    }
    return 0;
}

int main(int argc, const char** argv) {
    if (argc < 2) {
        PrintUsage(argv);
        return 42;
    }
    std::string mode = argv[1];
    if (mode == "train") {
        if (argc < 5) {
            PrintUsage(argv);
            return 42;
        }
        std::string alphabetFile = argv[2];
        std::string datasetFile = argv[3];
        std::string resultModelFile = argv[4];
        return Train(alphabetFile, datasetFile, resultModelFile);
    } else if (mode == "score") {
        if (argc < 3) {
            PrintUsage(argv);
            return 42;
        }
        std::string modelFile = argv[2];
        return Score(modelFile);
    } else if (mode == "scoredcands") {
        if (argc < 3) {
            PrintUsage(argv);
            return 42;
        }
        std::string modelFile = argv[2];
        return ScoredCands(modelFile);
    } else if (mode == "correct") {
        if (argc < 3) {
            PrintUsage(argv);
            return 42;
        }
        std::string modelFile = argv[2];
        return Correct(modelFile);
    } else if (mode == "fix") {
        if (argc < 5) {
            PrintUsage(argv);
            return 42;
        }
        std::string modelFile = argv[2];
        std::string inFile = argv[3];
        std::string outFile = argv[4];
        return Fix(modelFile, inFile, outFile);
    }

    PrintUsage(argv);
    return 42;
}
