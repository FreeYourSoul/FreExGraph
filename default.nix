let pkgs = import <nixpkgs> { };
in with pkgs; rec {

  freexgraph = (callPackage ./recipe.nix) { report_coverage = true; };

  
  build_env = python3.buildEnv.override {
    extraLibs = [
    	      freexgraph
    ];
    ignoreCollisions = true;
  };
  

}
