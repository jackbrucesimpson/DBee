# DBee

Now that my CSV dataset has grown to a couple of hundred GB, I'm rewriting it in two parts:

1. Scripts to process the data and insert it into a MySQL database.
2. Scripts to query the database and analyse the data.

## Structure

- src: Python scripts, packages and database schema.
- bin: Bash scripts to
    - insert_csv.sh: Runs CSV -> DB scripts with commandline arguments.
    - analyse_db.sh: Queries DB and analyses data.
- results:
