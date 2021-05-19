{ lib, buildPythonPackage, fetchPypi, flake8, beautifulsoup4, six }:

buildPythonPackage rec {
  pname = "markdownify";
  version = "0.7.4";

  src = fetchPypi {
    inherit pname version;
    sha256 = "Qkjdh9hvtVSY67Dje8bHsfVWW9gfDAKmuaBP+8DBKnQ=";
  };

  buildInputs = [ flake8 ];
  propagatedBuildInputs = [ beautifulsoup4 six ];

  doCheck = false;

  meta = with lib; {
    homepage = "https://github.com/matthewwithanm/python-markdownify";
    description = "Convert HTML to Markdown";
    license = licenses.mit;
  };
}
