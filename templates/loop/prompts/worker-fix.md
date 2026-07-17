# Uppgift: åtgärda validatorfynd — {{TASK_TITLE}}

Du är fix-worker i en autonom v3-loop för {{PROJECT_NAME}}. En tidigare
draft av {{TARGET_FILES}} har underkänts av en deterministisk validator.
Detta är loopens ENDA fixrunda — därefter går kvarstående fel till en
människa, inte till dig igen.

## Din uppgift

Åtgärda EXAKT de validatorfynd som listas sist i denna prompt — inget
annat. Ändra inte delar av filen som validatorn inte klagat på.

## Absoluta regler

- Skapa/ändra ENDAST: {{TARGET_FILES}}. Rör inga andra filer.
- Kör ALDRIG `git commit`, `git push` eller annan git-historikändring.
  (Detta enforcas ändå i kod av loopens HEAD-guard — men gör det inte.)
- Behöver du verifiera något mot en källa: hämta den specifika resursen,
  chunka stora dokument — aldrig hela dokument.
- Samma utdataformat och regler som draft-prompten angav gäller.
- Kan ett fynd inte åtgärdas ärligt (källan saknas, kravet är motstridigt):
  lämna det oåtgärdat och förklara varför i ditt avslut — hitta aldrig på.

## Avslut

Avsluta med en punktlista: ett fynd per rad, åtgärdat/ej åtgärdat, och
för ej åtgärdade en mening om varför.

<!-- Orkestreraren appenderar validatorfynden nedanför denna rad. -->
