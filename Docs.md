Blackboard Scraper downloads the entire structure of a blackboard course, and then recursively downloads items from the structure. This means that whether a file is chosen to be downloaded may depend on how the entire blackboard course appears, but it also means that the structure collection cannot depend on file content. This is assumed to be fine, since the structure is usually very small anyways.

Main: Coordinating the program and the downloading structure
Blackboard: Required code for extracting the structure and links from blackboard
Echo: Required code for downloading data from echo. Note that this uses its own download selection for now.
Base: Required base code for naming, downloading files, download selection, general useful code etc
