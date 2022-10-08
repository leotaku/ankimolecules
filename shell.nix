{ pkgs ? import <nixpkgs> { } }:
with pkgs;
stdenvNoCC.mkDerivation {
  name = "dev-shell";
  buildInputs =
    [ python3Packages.pandas pyright python3Full nodePackages.prettier ];
}
