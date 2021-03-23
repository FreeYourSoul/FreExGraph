let pkgs = import <nixpkgs> { };
in with pkgs; rec {

  freexgraph = (callPackage ./recipe.nix) { };

#  build_env = python38.buildEnv.override {
#    extraLibs = [ freexgraph ];
#    ignoreCollisions = true;
#  };
  
}
