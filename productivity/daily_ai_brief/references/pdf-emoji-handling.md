# Gestion des émojis dans la génération PDF (fpdf2)

Lors de la génération de PDF avec fpdf2 et la police DejaVu, certains émojis ne sont pas rendus correctement, ce qui peut entraîner des caractères manquants ou des erreurs de rendu.

## Approches recommandées

1. **Filtrage préalable** : Supprimer ou remplacer les émojis avant d'appeler `generate_pdf`.
   ```python
   import re
   emoji_pattern = re.compile(
       "["
       "\U0001F600-\U0001F64F"  # emoticons
       "\U0001F300-\U0001F5FF"  # symbols & pictographs
       "\U0001F680-\U0001F6FF"  # transport & map symbols
       "\U0001F1E0-\U0001F1FF"  # flags (iOS)
       "\U00002500-\U00002BEF"  # various symbols
       "\U00002702-\U000027B0"
       "\U00002702-\U000027B0"
       "\U000024C2-\U0001F251"
       "]+",
       flags=re.UNICODE,
   )
   clean_text = emoji_pattern.sub(r'', text)
   ```

2. **Substitution explicite** : Remplacer certains émojis par leurs équivalents texte (ex: `1️⃣` → `1.`, `📝` → `[note]`, `🔗` → `[lien]`, `💡` → `[idée]`).

3. **Utilisation de polices alternatives** : Si vous avez besoin de garder les émojis, envisagez d'utiliser une police qui les supporte (comme Noto Color Emoji) et de l'ajouter à fpdf2 via `add_font`. Cependant, cela augmente la taille du PDF et peut ne pas être supporté partout.

## Exemple d'intégration dans le script

Dans `scripts/generate_pdf.py`, ajoutez une fonction `sanitize_for_pdf` qui applique le filtrage ou la substitution, puis appelez-la sur le contenu avant de le passer à `parse_content`.

Consultez la référence pour des exemples complets.