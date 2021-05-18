{ lib, buildPythonPackage, fetchPypi, mypy, discordpy }:

buildPythonPackage rec {
  pname = "discord.py-stubs";
  version = "1.7.1";

  src = fetchPypi {
    inherit pname version;
    sha256 = "LebU6SPxIc2mLVBgidUsR4vRdo0nSA/h6quSBq9awqA=";
  };

  propagatedBuildInputs = [ mypy discordpy ];

  meta = with lib; {
    homepage = "https://github.com/bryanforbes/discord.py-stubs";
    description = "This package contains type stubs to provide more precise static types and type inference for discord.py.";
    license = licenses.bsd3;
    maintainers = with maintainers; [ syberant ];
  };
}
