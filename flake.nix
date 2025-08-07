{
  inputs = {
    nixpkgs.url = "github:cachix/devenv-nixpkgs/rolling";
    devenv.url = "github:cachix/devenv";
    devenv.inputs.nixpkgs.follows = "nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix.url = "github:pyproject-nix/uv2nix";
    uv2nix.inputs.nixpkgs.follows = "nixpkgs";
  };

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = "https://devenv.cachix.org";
  };

  outputs = {
    self,
    nixpkgs,
    devenv,
    flake-utils,
    pyproject-build-systems,
    pyproject-nix,
    uv2nix,
    ...
  } @ inputs:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      python = pkgs.python312;

      workspace = uv2nix.lib.workspace.loadWorkspace {workspaceRoot = self;};
      overlay = workspace.mkPyprojectOverlay {
        sourcePreference = "wheel";
      };

      # Use base package set from pyproject.nix builders
      pythonSet =
        (pkgs.callPackage pyproject-nix.build.packages {
          inherit python;
          stdenv = pkgs.stdenv.override {
            targetPlatform =
              pkgs.stdenv.targetPlatform
              // {
                # Sets MacOS SDK version to 15.5 which implies Darwin version 24.
                # See https://en.wikipedia.org/wiki/MacOS_version_history#Releases for more background on version numbers.
                darwinSdkVersion = "15.5";
              };
          };
        }).overrideScope
        (
          pkgs.lib.composeManyExtensions [
            pyproject-build-systems.overlays.default
            overlay
          ]
        );
    in {
      packages = {
        default = pythonSet.mkVirtualEnv "glados-tts" {glados-tts = ["cpu"];};

        # Alternative package with CUDA support
        cuda = pythonSet.mkVirtualEnv "glados-tts" {glados-tts = ["cuda"];};

        # Development environment
        dev = pythonSet.mkVirtualEnv "glados-tts" {glados-tts = ["dev" "cpu" "http"];};

        # HTTP server application
        http = pythonSet.mkVirtualEnv "glados-tts" {glados-tts = ["cpu" "http"];};
        devenv-up = self.devShells.${system}.default.config.procfileScript;
        devenv-test = self.devShells.${system}.default.config.test;
      };

      apps = {
        default = {
          type = "app";
          program = "${self.packages."${system}".http}/bin/glados-tts";
        };
      };

      devenv.shells.default = {
        inherit inputs pkgs;
        packages = with pkgs; [
          python312
          uv
        ];
        git-hooks.hooks = {
          # Nix code formatter
          alejandra = {
            enable = true;
            after = ["deadnix"];
          };
          # Removes nix dead code
          deadnix = {
            enable = true;
            args = ["--edit"];
          };
          black.enable = true;
        };
      };
    });
}
