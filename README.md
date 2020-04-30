# AGILE Reproducibility Reviews 2020

## About

This repository contains code used for the organisation and management of the reproducibility review at AGILE 2020.
Read more about the review process and the reproducibility committee here: [https://reproducible-agile.github.io/2020/#reproducibility-review.

To work on the main R Markdown file, `agile-2020-papers.Rmd`, run

```bash
make
```

and then open the Jupyter UI at the link shown in the console.
In the UI, go to "New" > "RStudio" to get an integrated development environment with the required dependencies.

The `Makefile`'s default target will create a virtual Python environment to execute [`repo2docker`](https://repo2docker.readthedocs.io/) using the files in this repository, notably `install.R` where you must add required R packages, and the `Dockerfile` where all system dependencies and remaining software is installed and configured.

## Reproducibility Reviews

The assignment of reviews is done via a privately shared 

## License

Copyright 2020 Daniel Nüst, published under The Apache License, Version 2.0.
