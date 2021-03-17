let pkgs = import <nixpkgs> { };
in with pkgs; rec {

  FreExGraph = (callPackage ./recipe.nix) { };

}
