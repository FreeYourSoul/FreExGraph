{ lib, python38, python38Packages, nix-gitignore, use_revision ? null }:

python38.pkgs.buildPythonPackage rec {
  pname = "freexgraph";
  version = "0.1.0";

  src = if (builtins.isNull use_revision || use_revision == "") then
    nix-gitignore.gitignoreSource [ ".git" ] ./.
  else
    builtins.fetchGit {
      url = "https://github.com/FreeYourSoul/FreExGraph";
      rev = use_revision;
    };

  checkInputs = [ python38Packages.pytest ];
  propagatedBuildInputs = with python38Packages; [ networkx tqdm ];

  doCheck = true;

  checkPhase = ''
    python -m pytest
  '';

  meta = with lib; {
    homepage = "https://github.com/pytoolz/toolz";
    description = "Execution graph handling tools";
    license = licenses.mit;
  };
}
