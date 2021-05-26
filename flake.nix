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
      }) // {
        packages.x86_64-linux.docker =
          let pkgs = nixpkgs.legacyPackages.x86_64-linux;
          in pkgs.dockerTools.buildImage {
            name = "patrick";
            fromImage = pkgs.dockerTools.pullImage {
              imageName = "alpine";
              imageDigest =
                "sha256:69e70a79f2d41ab5d637de98c1e0b055206ba40a8145e7bddb55ccc04e13cf8f";
              sha256 = "CWjvHtsusvx79z9+lo+UMLS1nHX3q21c0R2Ch1eBsjw=";
              finalImageTag = "3.13.5";
              finalImageName = "alpine";
            };
            config = { Cmd = [ "${self.defaultPackage.x86_64-linux}/bin/patrick" ]; };
          };
      };
}
