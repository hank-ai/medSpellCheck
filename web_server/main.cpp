#include "jamspell/spell_corrector.hpp"
#include "contrib/httplib/httplib.h"
#include "contrib/nlohmann/json.hpp"
#include <cwctype>
//#include "contrib/libssl64MT.lib"
//#include <libcrypto>

#define CPPHTTPLIB_OPENSSL_SUPPORT

std::string GetCandidatesScored(const NJamSpell::TSpellCorrector& corrector,
                          const std::string& text)
{
    return corrector.GetALLCandidatesScoredJSON(text);
}

std::string FixText(const NJamSpell::TSpellCorrector& corrector,
                    const std::string& text)
{
    std::wstring input = NJamSpell::UTF8ToWide(text);
    return NJamSpell::WideToUTF8(corrector.FixFragment(input));
}

int main(int argc, const char** argv) {
    if (argc < 4 || argc > 7) {
        std::cerr << "(error) Arg count = " << argc << std::endl;
        std::cerr << "Usage: " << argv[0] << " model.bin localhost 8080 [sslcertpath] [sslkeypath]\n";
        std::cerr << "   Note: SSL isn't currently working tho\n";
        return 42;
    }

    std::string modelFile = argv[1];
    std::string hostname = argv[2];
    int port = std::stoi(argv[3]);
    std::string sslcert;
    std::string sslkey;
    if(argc == 6) {
        sslcert = argv[4];
        sslkey = argv[5];
        std::cerr << "[info] received ssl request (" << sslcert << " | " << sslkey << ")\n";
    }


    NJamSpell::TSpellCorrector corrector;
    if (!corrector.LoadLangModel(modelFile)) {
        std::cerr << "[error] failed to load model" << std::endl;
        return 42;
    }

    //if (argc < 6){ 
        httplib::Server srv; 
    //    }
    //else { httplib::SSLServer srv(sslcert, sslkey)}
    
    srv.Get("/fix", [&corrector](const httplib::Request& req, httplib::Response& resp) {
        resp.set_content(FixText(corrector, req.get_param_value("text")) + "\n", "text/plain");
    });

    srv.Post("/fix", [&corrector](const httplib::Request& req, httplib::Response& resp) {
        resp.set_content(FixText(corrector, req.body) + "\n", "text/plain");
    });

    srv.Get("/candidates", [&corrector](const httplib::Request& req, httplib::Response& resp) {
        resp.set_content(GetCandidatesScored(corrector, req.get_param_value("text")) + "\n", "text/plain");
    });

    srv.Post("/candidates", [&corrector](const httplib::Request& req, httplib::Response& resp) {
        resp.set_content(GetCandidatesScored(corrector, req.body) + "\n", "text/plain");
    });

    std::cerr << "[info] starting web server at " << hostname << ":" << port << std::endl;
    srv.listen(hostname.c_str(), port);
    return 0;
}
