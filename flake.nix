{
  description = "R&D Project 2020-2021, Discord bot assisting in seminars";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonPackages = pkgs.python3Packages.override {
          overrides = final: prev: {
            discord-stubs = final.callPackage ./discord-py-stubs.nix { };
            markdownify = final.callPackage ./markdownify.nix { };
          };
        };
        r-and-d-discord-bot = pkgs.callPackage ./r-and-d-discord-bot.nix {
          python3Packages = pythonPackages;
        };
      in rec {
        defaultPackage = r-and-d-discord-bot;
        packages.r-and-d-discord-bot = r-and-d-discord-bot;

        defaultApp = {
          type = "app";
          program = "${r-and-d-discord-bot}/bin/r_and_d_discord_bot";
        };
        apps.r-and-d-discord-bot = defaultApp;

        devShell = pkgs.mkShell {
          buildInputs = (defaultPackage.propagatedBuildInputs or [ ])
            ++ (with pythonPackages; [
              python-language-server
              autopep8
              flake8
            ]);
        };

        apps = {
          lint = {
            type = "app";
            program = "" + pkgs.writeScript "lint" ''
              ${pythonPackages.flake8}/bin/flake8 ./r_and_d_discord_bot
            '';
          };

          test = {
            type = "app";
            program = "" + pkgs.writeScript "test" ''
              ${pythonPackages.mypy}/bin/mypy --namespace-packages ./r_and_d_discord_bot --python-executable ${
              # TODO: this is ugly
                pythonPackages.python.withPackages
                (ps: with ps; [ pythonPackages.discord-stubs ])
              }/bin/python3
            '';
          };
        };
      });
}
