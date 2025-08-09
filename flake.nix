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
      packages =
        rec {
          default = pkgs.stdenv.mkDerivation rec {
            name = "glados-tts";
            src = ./.;

            gladosModel = pkgs.fetchurl {
              url = "https://github.com/dnhkng/GlaDOS/releases/download/0.1/glados.onnx";
              sha256 = "17ea16dd18e1bac343090b8589042b4052f1e5456d42cad8842a4f110de25095";
            };

            phonemizerModel = pkgs.fetchurl {
              url = "https://github.com/dnhkng/GlaDOS/releases/download/0.1/phomenizer_en.onnx";
              sha256 = "b64dbbeca8b350927a0b6ca5c4642e0230173034abd0b5bb72c07680d700c5a0";
            };

            pythonEnv = pythonSet.mkVirtualEnv name {glados-tts = ["cpu"];};

            buildInputs = [pythonEnv];

            buildPhase = ''
              mkdir -p $out/models/TTS

              # Copy model configuration file
              cp -r $src/models/TTS/glados.onnx.json $out/models/TTS/

              cp $gladosModel $out/models/TTS/glados.onnx
              cp $phonemizerModel $out/models/TTS/phomenizer_en.onnx
            '';

            installPhase = ''
              mkdir -p $out/bin
              # Copy all binaries except for glados-tts
              for f in $pythonEnv/bin/*; do
                [ "$(basename "$f")" = "glados-tts" ] && continue
                cp "$f" $out/bin/
              done

              # Create wrapper script for glados-tts
              cat > $out/bin/glados-tts << EOF
              #!/bin/bash
              export GLADOS_TTS_MODELS_DIR="$out/models/TTS"
              exec $pythonEnv/bin/glados-tts "\$@"
              EOF
              chmod +x $out/bin/glados-tts
            '';
          };

          # The version of python packaged with glados-tts
          python = python;

          # Development environment
          dev = self.packages.${system}.default.overrideAttrs (oldAttrs: {
            pythonEnv = pythonSet.mkVirtualEnv oldAttrs.name {glados-tts = ["dev" "cpu" "http"];};
          });

          # HTTP server applications
          cpu-http = self.packages.${system}.default.overrideAttrs (oldAttrs: {
            pythonEnv = pythonSet.mkVirtualEnv oldAttrs.name {glados-tts = ["cpu" "http"];};
          });
          # Minimal Docker image
          docker-cpu-http = let
            inherit cpu-http;
          in
            pkgs.dockerTools.buildLayeredImage {
              name = "glados-tts";
              tag = "docker-cpu-http";

              contents = [
                cpu-http
              ];

              config = {
                Cmd = ["${cpu-http}/bin/glados-tts"];
                ExposedPorts = {
                  "8124/tcp" = {};
                };
                Env = [
                  "PATH=${cpu-http}/bin"
                  "GLADOS_TTS_MODELS_DIR=${cpu-http}/models/TTS"
                ];
              };
            };
        }
        // pkgs.lib.optionalAttrs (system != "aarch64-darwin") {
          # CUDA packages - excluded on macOS ARM due to compatibility issues
          cuda-cli = self.packages.${system}.default.overrideAttrs (oldAttrs: {
            pythonEnv = pythonSet.mkVirtualEnv oldAttrs.name {glados-tts = ["cuda" "cli"];};
          });

          cuda-http = self.packages.${system}.default.overrideAttrs (oldAttrs: {
            pythonEnv = pythonSet.mkVirtualEnv oldAttrs.name {glados-tts = ["cuda" "http"];};
          });

          # CUDA Docker image
          docker-cuda = pkgs.dockerTools.buildLayeredImage {
            name = "glados-tts";
            tag = "cuda";

            contents = [
              self.packages.${system}.cuda-http
              pkgs.bash
              pkgs.coreutils
            ];

            config = {
              Cmd = ["${self.packages.${system}.cuda-http}/bin/glados-tts"];
              ExposedPorts = {
                "8124/tcp" = {};
              };
              Env = [
                "PATH=${self.packages.${system}.cuda-http}/bin:${pkgs.bash}/bin:${pkgs.coreutils}/bin"
              ];
            };
          };
        };

      apps = {
        default = {
          type = "app";
          program = "${self.packages."${system}".cpu-http}/bin/glados-tts";
          meta = {
            description = "GlaDOS TTS application with HTTP server";
            maintainers = with pkgs.lib.maintainers; [teekennedy];
            # glados TTS model and config are MIT licenced, but piper's http server is GPL3
            license = pkgs.lib.licenses.gpl3plus;
            homepage = "https://github.com/dnhkng/GLaDOS";
            platform = pkgs.lib.platforms.all;
          };
        };
      };

      devShells.default = devenv.lib.mkShell {
        inherit inputs pkgs;
        modules = [
          ({pkgs, ...}: {
            # This is your devenv configuration
            packages = [
              python
              pkgs.uv
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
          })
        ];
      };
    });
}
