# Review reports 

## Contents of this folder

If reproducibility reviewers choose to publish the report source files or other configurations created for the reproduction, they can do so here.

Please make sure not to commit any large files, or files that should not be re-published.
Use the OSF project for large files.

## CODECHECK

The codecheck configuration files to include the AGILE reproducibility reviews in the [register of CODECHECKs](https://codecheck.org.uk/register/) may be stored here, in addition to the respective online repository, see [register README](https://github.com/codecheckers/register/blob/master/README.md) for details.

## File format conversion

Ideally, the files here use text-based formats, such as (R) Markdown.
You can use pandoc to convert to and from other formats, e.g. for `.docx`:

```
pandoc 2020-012/reproreview-paper_012.docx --to markdown --from docx --output 2020-012/reproreview-paper_012.md
```
