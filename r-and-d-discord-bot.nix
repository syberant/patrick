{ lib, python3Packages }:

python3Packages.buildPythonApplication {
  pname = "r-and-d-discord-bot";
  version = "0.0.1";

  doCheck = false;

  src = ./.;

  propagatedBuildInputs = with python3Packages; [ discordpy ];

  meta = with lib; {
    homepage = "https://github.com/syberant/r-and-d-discord-bot";
    description = "R&D Project 2020-2021, Discord bot assisting in seminars";
    # license = licenses.TODO
    maintainers = with maintainers; [ syberant ];
  };
}
