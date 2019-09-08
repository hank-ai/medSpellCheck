%module jamspell
%include "std_vector.i"
%include "pyabc.i"
%include <std_list.i>
%include <std_string.i>
%include <std_wstring.i>
%{
#include "jamspell/spell_corrector.hpp"
#include "jamspell/utils.hpp"
%}

//TScoredWords = vector<TScoredWord>;

// Instantiate templates used by example
namespace std {
   %template(StringVector) vector<wstring>;
}

%include "jamspell/spell_corrector.hpp"
#include "jamspell/utils.hpp"