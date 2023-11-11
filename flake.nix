{
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs?ref=3476a10478587dec90acb14ec6bde0966c545cc0";
    poetry2nix.url = "github:nix-community/poetry2nix";
    poetry2nix.inputs.flake-utils.follows = "flake-utils";
    poetry2nix.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    poetry2nix,
  }:
    {
      # Nixpkgs overlay providing the application
      overlay = nixpkgs.lib.composeManyExtensions [
        poetry2nix.overlay
        (final: prev: {
          hyperer = prev.poetry2nix.mkPoetryApplication {
            projectDir = ./.;
            # checkGroups Default is [ "dev" ]. We remove that to keep from installing ruff as a nix dep, which is broken currently
            checkGroups = [];
          };
        })
      ];
    }
    // (flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {
        inherit system;
        overlays = [self.overlay];
      };
    in {
      packages.default = pkgs.hyperer;

      devShell = pkgs.mkShell {
        buildInputs = with pkgs; [poetry python39 cargo];
      };
    }));
}
