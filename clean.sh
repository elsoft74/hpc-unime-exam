#!/bin/bash

# Percorso della cartella da esaminare
cartella="/nfs"
echo "Removing json files in $cartella"
# Comando per elencare i file con estensione .json nella cartella specificata
elenco_file=$(find "$cartella" -maxdepth 1 -type f -name "*.json")

# Ciclo per ogni file trovato
for file in $elenco_file; do
  # Comando per eliminare il file
  rm -f "$file"
#echo "removed $file"
done

# Messaggio di conferma
echo "All JSONs in $cartella removed."
