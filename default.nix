let pkgs = import <nixpkgs> { };
in with pkgs; rec {

  freexgraph = (callPackage ./recipe.nix) { report_coverage = true; };

}
