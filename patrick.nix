{ lib, python3Packages }:

python3Packages.buildPythonApplication {
  pname = "patrick";
  version = "1.0.0";

  doCheck = false;

  src = ./.;

  propagatedBuildInputs = with python3Packages; [
    discordpy
    beautifulsoup4
    markdownify
    requests
  ];

  meta = with lib; {
    homepage = "https://github.com/syberant/patrick";
    description = "R&D Project 2020-2021, Discord bot assisting in seminars";
    license = licenses.gpl3;
    maintainers = with maintainers; [ syberant ];
  };
}
