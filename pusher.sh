#!/bin/bash

# Fonction pour pousser chaque fichier un par un
push_each_file() {
    for file in $(git ls-files --modified --others --exclude-standard); do
        # Exclure les fichiers temporaires et binaires
        if [[ "$file" != *.o && "$file" != *~ && "$file" != *.bin ]]; then
            # Ajouter le fichier modifié
            git add "$file"
            
            # Commiter avec le format de message demandé
            commit_message="[add] '$file' file"
            git commit -m "$commit_message"
            
            # Pousser le commit
            git push
            
            # Afficher un message pour indiquer que le fichier a été poussé
            echo "Fichier $file poussé avec succès"
        else
            echo "Fichier $file ignoré"
        fi
    done
}

# Appel de la fonction
push_each_file
