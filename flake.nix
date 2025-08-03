{
  description = "Text-to-Speech synthesis package with GLaDOS and Kokoro voices";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    uv2nix.url = "github:pyproject-nix/uv2nix";
    uv2nix.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    uv2nix,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};

      workspace = uv2nix.lib.${system}.loadWorkspace {workspaceRoot = ./.;};
    in {
      packages = {
        default = workspace.mkVirtualEnv "glados-tts" {
          extras = ["cpu"]; # Use CPU by default, can be overridden
        };

        # Alternative package with CUDA support
        cuda = workspace.mkVirtualEnv "glados-tts" {
          extras = ["cuda"];
        };

        # Development environment
        dev = workspace.mkVirtualEnv "glados-tts" {
          extras = ["cpu" "dev"];
        };
      };

      devShells.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          python312
          uv
        ];
        shellHook = ''
          echo "TTS Package development environment"
          echo "Run 'uv sync' to install dependencies"
        '';
      };
    });
}
