{
  description = "GLaDOS TTS";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    devenv.url = "github:cachix/devenv";
    devenv.inputs.nixpkgs.follows = "nixpkgs";
    nixpkgs-python.url = "github:cachix/nixpkgs-python";
    nixpkgs-python.inputs = {nixpkgs.follows = "nixpkgs";};
  };

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = "https://devenv.cachix.org";
  };

  outputs = inputs @ {flake-parts, ...}:
    flake-parts.lib.mkFlake {
      inherit inputs;
    } {
      imports = [
        inputs.devenv.flakeModule
      ];
      systems = ["aarch64-darwin" "x86_64-linux"];
      perSystem = {
        config,
        self',
        inputs',
        pkgs,
        lib,
        system,
        ...
      }: {
        devenv.shells.default = {
          # https://devenv.sh/packages/
          packages = with pkgs; [
            git-lfs
          ];

          enterShell = ''
          '';

          # https://devenv.sh/languages/
          languages.nix.enable = true;
          languages.python.enable = true;
          languages.python.version = "3.12";
          languages.python.poetry.enable = true;
          languages.python.poetry.activate.enable = true;
          languages.python.poetry.install.enable = true;
          languages.python.poetry.install.verbosity = "little";
          languages.python.poetry.install.onlyInstallRootPackage = true;

          # https://devenv.sh/scripts/
          # scripts.hello.exec = "echo hello from $GREET";

          # https://devenv.sh/pre-commit-hooks/
          pre-commit.hooks = {
            # Nix code formatter
            alejandra.enable = true;
            # Terraform code formatter
            terraform-format.enable = true;
            # YAML linter
            yamllint.enable = true;
          };

          # https://devenv.sh/processes/
          # processes.ping.exec = "ping example.com";
        };
        packages = {
        };
      };

      flake = {
        colmena = {
          meta = {
            description = "K3s cluster";
            nixpkgs = import inputs.nixpkgs {
              system = "x86_64-linux";
              overlays = [];
            };
            specialArgs = {
              inherit inputs;
              nixpkgs-master = import inputs.nixpkgs-master {
                system = "x86_64-linux";
                overlays = [];
              };
            };
          };

          defaults = {
            imports = [
              ./modules/common
              ./modules/k3s
            ];
          };

          borg-0 = {
            name,
            nodes,
            pkgs,
            ...
          }: {
            imports = [
              ./hosts/borg-0
            ];
            deployment = {
              tags = [];
              # Copy the derivation to the target node and initiate the build there
              buildOnTarget = true;
              targetUser = null; # Defaults to $USER
              targetHost = "borg-0.lan";
            };

            services.k3s = {
              role = "server";
              # Leave true for first node in cluster
              clusterInit = true;
            };
            sops.secrets.tkennedy_hashed_password = {
              neededForUsers = true;
            };
          };
        };
      };
    };
}
