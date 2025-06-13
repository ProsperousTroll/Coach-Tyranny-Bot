{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    (pkgs.python312.withPackages (ps: with ps; [
      discordpy
      python-dotenv
      # Add other Python dependencies here, e.g. ps.requests, ps.aiohttp, etc.
    ]))
  ];
}

