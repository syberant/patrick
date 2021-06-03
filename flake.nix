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
        packageOverrides = final: prev: {
          discord-stubs = final.callPackage ./discord-py-stubs.nix { };
          markdownify = final.callPackage ./markdownify.nix { };
        };
        pythonPackages =
          pkgs.python3Packages.override { overrides = packageOverrides; };
        python = pythonPackages.python.override { inherit packageOverrides; };

        patrick = pkgs.callPackage ./patrick.nix {
          python3Packages = pythonPackages;
        };
      in rec {
        defaultPackage = patrick;
        packages.patrick = patrick;

        defaultApp = {
          type = "app";
          program = "${patrick}/bin/patrick";
        };
        apps.patrick = defaultApp;

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
              ${pythonPackages.flake8}/bin/flake8 ./patrick
            '';
          };

          test = {
            type = "app";
            program = "" + pkgs.writeScript "test" ''
              ${pythonPackages.mypy}/bin/mypy --namespace-packages ./patrick --python-executable ${
                python.withPackages (ps: with ps; [ discord-stubs ])
              }/bin/python3
            '';
          };
        };
      });
}
