{
  "source": "HUG_CompatAdm_DCI",
  "type": "IV_Y_SITE_COMPATIBILITY",
  "last_update": "2018 (HUG source referenced)",

  "rules": [
    "Compatibilité évaluée par paires uniquement",
    "Concentrations usuelles obligatoires",
    "Solvant doit être compatible avec les deux médicaments",
    "Absence de donnée = ne pas conclure compatibilité",
    "Ne pas perfuser ensemble acides et bases sans données"
  ],

  "codes": {
    "C": "compatible",
    "I": "incompatible",
    "Cg": "compatible avec conditions",
    "Ca": "compatible selon concentration",
    "Cb": "compatible mais vigilance",
    "Cc": "données limitées",
    "Cd": "variable selon conditions",
    "Ce": "test laboratoire",
    "Cf": "non applicable / données insuffisantes"
  },

  "drugs": [
    {
      "name": "ACICLOVIR",
      "ph": 11,
      "compatibility_notes": "haut pH, surveillance précipitation"
    },
    {
      "name": "ADRENALINE",
      "synonym": "EPINEPHRINE",
      "ph": "2.5-5.0",
      "notes": "vasopresseur critique ICU"
    },
    {
      "name": "AMIODARONE",
      "ph": "3.5-4.5",
      "notes": "incompatibilités fréquentes selon concentration"
    },
    {
      "name": "MIDAZOLAM",
      "ph": "3-4",
      "notes": "sédation ICU, compatibilité variable selon dilution"
    },
    {
      "name": "NORADRENALINE",
      "notes": "vasopresseur critique, perfusion dédiée recommandée"
    }
  ],

  "compatibility_rules_general": [
    "pH acide + base = risque précipitation",
    "Toujours vérifier concentration finale",
    "Perfusions critiques = ligne dédiée recommandée",
    "Nutrition parentérale souvent incompatible avec médicaments IV",
    "Sang et dérivés sanguins toujours seuls"
  ]
}
