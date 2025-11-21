# karp-resource-fula-ordboken

Scripts for preparing Fula Ordboken for Karp-backend

## Usage

1. Activate virtualenv: `source .venv/bin/activate`
2. Put the file you got somewhere, preferly in `data/data_raw`
   The file has the name `Fula Ordboken - export YYYY-MM-DD.zip`
3. Run `resource-fula-ordboken package-raw 'data/data_raw/Fula Ordboken - export YYYY-MM-DD.zip'`
   This will package the original file as SimpleArchive for Metadata Repo.
4. Run `resource-fula-ordboken raw2clean 'data/data_raw/Fula Ordboken - export YYYY-MM-DD.zip'`
   This will clean (and convert to utf-8 if needed) and package and place the the archive in `data/data_clean`
5. Run `resource-fula-ordboken clean2karp 'data/data_clean/fula_ordboken-export_YYYY-MM-DD.clean.saf.zip'`.
   This will convert Fula Ordboken to Karp format and package and place the the archive in `data/data_processed`.
   This will output entries to import in Karp and also the entries in a SimpleArchive.
