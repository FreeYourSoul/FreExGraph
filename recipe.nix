{ curl, lib, python38, python38Packages, nix-gitignore, use_revision ? null
, report_coverage ? false }:

python38.pkgs.buildPythonPackage rec {
  pname = "freexgraph";
  version = "1.2.3";

  src = if (builtins.isNull use_revision || use_revision == "") then
    nix-gitignore.gitignoreSource [ ".git" ] ./.
  else
    builtins.fetchGit {
      url = "https://github.com/FreeYourSoul/FreExGraph";
      rev = use_revision;
    };

  checkInputs = [ python38Packages.pytest python38Packages.coverage curl ];
  propagatedBuildInputs = with python38Packages; [ networkx tqdm ];

  doCheck = true;

  checkPhase = ''
    python -m pytest
  '';

  pythonImportsCheck = [ "freexgraph" ];

  meta = with lib; {
    homepage = "https://github.com/pytoolz/toolz";
    description = "Execution graph handling tools";
    license = licenses.mit;
  };
}
