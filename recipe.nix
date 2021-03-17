{ lib, buildPythonPackage, python38Packages, nix-gitignore, use_revision ? null }:

buildPythonPackage rec {
  pname = "FreExGraph";
  version = "0.1.0";

  src = if (builtins.isNull use_revision || use_revision == "") then
    nix-gitignore.gitignoreSource [ ".git" ] ./.
  else
    builtins.fetchGit {
      url = "https://github.com/FreeYourSoul/FreExGraph";
      rev = use_revision;
    };

  checkInputs = [ pytest ];
  propagatedBuildInputs = with python38Packages; [ networkx tqdm ];

  doCheck = false;

  meta = with lib; {
    homepage = "https://github.com/pytoolz/toolz";
    description = "Execution graph handling tools";
    license = licenses.bsd3;
    maintainers = with maintainers; [ fridh ];
  };
}