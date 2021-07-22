Blackboard Scraper downloads the entire structure of a blackboard course, and then recursively downloads items from the structure. This means that whether a file is chosen to be downloaded may depend on how the entire blackboard course appears, but it also means that the structure collection cannot depend on file content. This is assumed to be fine, since the structure is usually very small anyways.

main: Coordinating the program
blackboard: Basic structure for handling the copying and downloading of the program. Outsources all actual scraping/html work to Extractors and Downloaders
FolderExtractors/\*: Contains FolderExtractor plugins. See blackboard.py for documentation
LinkExtractors/\*: Contains LinkExtractor plugins. See blackboard.py for documentation
base: Required base code for naming, downloading files, download selection, general useful code etc
