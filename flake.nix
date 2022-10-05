{
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/fd7a18259e351055b656f2cb1260d831edb9dd57";
    poetry2nix.url = "github:nix-community/poetry2nix";
    poetry2nix.inputs.flake-utils.follows = "flake-utils";
    poetry2nix.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    {
      # Nixpkgs overlay providing the application
      overlay = nixpkgs.lib.composeManyExtensions [
        poetry2nix.overlay
        (final: prev: {
          hyperer = prev.poetry2nix.mkPoetryApplication {
            projectDir = ./.;
          };
        })
      ];
    } // (flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlay ];
        };
      in
      {
        packages.default = pkgs.hyperer;

        devShell = pkgs.mkShell { 
          buildInputs = [ pkgs.python3 pkgs.poetry ];
        };
      }));
}
