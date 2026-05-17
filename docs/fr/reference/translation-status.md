# État des traductions

FastAPI-fastkit publie sa documentation dans plusieurs langues, mais ces traductions **n'avancent pas toutes au même rythme**. Cette page est la référence principale pour savoir ce qui est réellement traduit, ce qui s'affiche lorsqu'une page ne l'est pas encore et comment contribuer.

## Source de vérité

> **L'anglais (`en`) est la référence principale.** Tous les comportements du produit, du CLI et de l'API décrits dans la documentation sont d'abord rédigés dans les fichiers anglais. Les autres locales sont des traductions de cette base anglaise et peuvent prendre du retard par rapport à une version.
>
> Si une page traduite contredit la page anglaise, **faites confiance à la page anglaise** jusqu'à ce que la traduction soit mise à jour.

Les fichiers anglais se trouvent sous [`docs/en/`](https://github.com/bnbong/FastAPI-fastkit/tree/main/docs/en). Toutes les autres locales (`docs/ko/`, `docs/ja/`, …) sont des cibles de traduction.

Le `CHANGELOG.md` à la racine du dépôt fait aussi partie de cette référence anglaise. Des pages locales `changelog.md` peuvent exister comme pages d'accès, mais elles réutilisent volontairement l'historique de versions canonique en anglais au lieu d'en maintenir des copies traduites.

## Complétude par locale

Les nombres ci-dessous comptent les pages Markdown dans l'arborescence de chaque locale par rapport à la source anglaise. Ils reflètent ce qui est réellement présent dans le dépôt — pas ce qui apparaît dans le sélecteur de langue (la section suivante l'explique).

| Locale | État | Pages Markdown | Notes |
|---|---|---:|---|
| 🇬🇧 Anglais (`en`) | ✅ Source de vérité | 26 / 26 | Référence. |
| 🇰🇷 Coréen (`ko`) | ✅ Complet | 26 / 26 | Toutes les pages de la locale sont présentes. Phase 1 : top-level + cœur du guide de l'utilisateur ; Phase 2 : reste du guide de l'utilisateur + tous les tutoriels ; Phase 3 : pages de contribution + de référence. `docs/ko/changelog.md` réutilise intentionnellement le `CHANGELOG.md` canonique en anglais. |
| 🇯🇵 Japonais (`ja`) | ✅ Complet | 26 / 26 | Toutes les pages de la locale sont présentes. Phase 1 : top-level + cœur du guide de l'utilisateur ; Phase 2 : reste du guide de l'utilisateur + tous les tutoriels ; Phase 3 : pages de contribution + de référence. `docs/ja/changelog.md` réutilise intentionnellement le `CHANGELOG.md` canonique en anglais. |
| 🇨🇳 Chinois (`zh`) | 🔴 Squelette | 0 / 26 | Cible de build uniquement. Toutes les pages retombent sur l'anglais. |
| 🇪🇸 Espagnol (`es`) | ✅ Complet | 26 / 26 | Toutes les pages de la locale sont présentes. Phase 1 : top-level + cœur du guide de l'utilisateur ; Phase 2 : reste du guide de l'utilisateur + tous les tutoriels ; Phase 3 : pages de contribution + de référence. `docs/es/changelog.md` réutilise intentionnellement le `CHANGELOG.md` canonique en anglais. |
| 🇫🇷 Français (`fr`) | ✅ Complet | 26 / 26 | Toutes les pages de la locale sont présentes. Phase 1 : top-level + cœur du guide de l'utilisateur ; Phase 2 : reste du guide de l'utilisateur + tous les tutoriels ; Phase 3 : pages de contribution + de référence. `docs/fr/changelog.md` réutilise intentionnellement le `CHANGELOG.md` canonique en anglais. |
| 🇩🇪 Allemand (`de`) | ✅ Complet | 26 / 26 | Toutes les pages de la locale sont présentes. Phase 1 : top-level + cœur du guide de l'utilisateur ; Phase 2 : reste du guide de l'utilisateur + tous les tutoriels ; Phase 3 : contributing + reference. `docs/de/changelog.md` réutilise intentionnellement le `CHANGELOG.md` canonique en anglais. |

*Instantané vérifié le 2026-05-17 ; la ligne `de` a été recomptée sur la branche actuelle après la fin de la Phase 3 (contributing + reference). L'allemand comporte désormais toutes les pages de la locale et `docs/de/changelog.md` pointe vers le changelog canonique en anglais.* Ces compteurs sont maintenus à la main ; pour recompter l'état actuel depuis la racine du dépôt, exécutez :

```console
$ for loc in en ko ja zh es fr de; do
    echo "$loc: $(find docs/$loc -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
  done
```

Si le recomptage ne correspond pas au tableau, c'est que le tableau est obsolète — mettez-le à jour (ou ouvrez une PR / un ticket signalant l'écart).

Légende :

- ✅ **Langue source** — la locale dans laquelle on écrit en premier.
- 🟡 **Partiel** — certaines pages sont traduites ; les pages manquantes retombent sur l'anglais.
- 🔴 **Squelette** — l'entrée du sélecteur de langue existe, mais aucune page traduite n'est encore livrée. Le site rend le contenu anglais sous les libellés de navigation traduits.

## Comment fonctionne le repli

Le site de documentation utilise [`mkdocs-static-i18n`](https://github.com/ultrabug/mkdocs-static-i18n) avec `fallback_to_default: true`. Cela signifie :

- Pour chaque locale traduite, MkDocs n'écrit que les pages présentes dans le répertoire de cette locale.
- Pour chaque page **absente** d'une locale, le build retombe sur la version anglaise de cette page.
- Le sélecteur de langue global liste toujours toutes les locales configurées, peu importe le nombre de pages que chacune contient, car le build produit une URL accessible pour chaque cas (page traduite ou, à défaut, repli anglais).

Ainsi, une entrée 🔴 Squelette dans le sélecteur de langue **ne signifie pas** que la documentation est traduite — seulement que la cible de build de la locale est configurée. Ce comportement est intentionnel (les contributeurs externes peuvent traduire une page à la fois sans casser le maillage de liens), mais il donne l'impression que le sélecteur de langue est plus complet que ne l'est réellement le contenu sous-jacent.

## Comment lire le site

- **Par défaut, restez en anglais** si vous voulez l'information la plus précise et la plus à jour.
- **Utilisez une locale traduite** uniquement après avoir consulté l'état de cette locale sur cette page. Si l'état est 🟡 ou 🔴 et que vous tombez sur un sujet non traduit, vous lisez en réalité un repli anglais sous un libellé de navigation traduit.

## Comment aider

L'organisation actuelle repose sur **un ticket de suivi par locale**, avec un travail découpé en **phases**. Par exemple, `ko` a été traité en Phase 1 (pages principales + cœur du guide utilisateur), en Phase 2 (reste du guide utilisateur + tous les tutoriels) puis en Phase 3 (pages de contribution + de référence). Chaque phase arrive dans sa propre PR, afin que les relecteurs puissent valider un ensemble cohérent sans attendre que toute la locale soit terminée.

Si vous souhaitez contribuer :

1. Lisez le [Guide de traduction](../contributing/translation-guide.md) pour le flux de travail, l'outillage et les conventions de style.
2. **Vérifiez ou ouvrez d'abord le ticket de suivi de la locale.** Si une locale a déjà un ticket de suivi ouvert, réservez-y une phase (ou une page précise d'une phase) pour éviter les doublons. S'il n'existe pas de ticket de suivi pour la locale qui vous intéresse, ouvrez-en un qui liste les pages appartenant à chaque phase, puis commencez par la Phase 1.
3. **L'idéal est une PR par phase.** Des PR plus petites du type « corriger cette seule page » restent les bienvenues, surtout pour corriger une traduction désynchronisée. Mais pour lancer une nouvelle locale, regrouper le travail par phase aide à garder un glossaire et des liens formulés de manière cohérente au sein du même ensemble.
4. Ouvrez la PR en ajoutant les fichiers sous `docs/<locale>/<même chemin>`. Conservez des noms de fichiers identiques à la source anglaise pour que MkDocs les détecte automatiquement.
5. Traitez les pages de changelog localisées comme des pages d'accès vers le `CHANGELOG.md` canonique en anglais, sauf si la politique du projet change explicitement.
6. Mettez à jour le tableau de cette page pour refléter le nouveau niveau de couverture (utilisez l'extrait de recomptage en haut de cette page) et mettez à jour la date « Instantané vérifié » pour que les relecteurs sachent quand la vérification a été faite pour la dernière fois. Indiquez dans la colonne « Notes » quelle phase est terminée si la locale est encore partielle.

Les signalements de bogues concernant des pages traduites désynchronisées par rapport à la source anglaise sont les bienvenus — merci de relier la page anglaise et la page traduite pour faciliter le triage.

## Pourquoi publier malgré tout des locales 🔴 Squelette

Deux raisons :

1. **Espace d'URL prévisible.** Chaque locale a déjà son sous-arbre `/<locale>/` accessible, de sorte que lorsqu'une page traduite arrive, le lien est stable dès le premier jour — y compris les liens publiés dans ce guide.
2. **Moins de friction pour les contributeurs.** Les personnes qui traduisent une seule page n'ont pas besoin, en plus, de configurer une nouvelle cible de build dans MkDocs : il leur suffit d'ajouter le fichier.

Si une locale reste en 🔴 Squelette sans activité de contribution pendant une période prolongée, nous pourrons reconsidérer le maintien de sa cible de build. Cette décision est suivie séparément et **n'est pas** quelque chose que cette page de statut modifie silencieusement.
