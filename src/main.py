import logging
import sys
import shutil
from os import makedirs
from os.path import basename, join as path_join
from json import loads as json_loads
from zipfile import ZipFile
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.parse import urlsplit
from pathlib import Path

BASE_URL = "https://www.curseforge.com/api/v1/mods/{projectID}/files/{fileID}"

def extractZip(zip_path, output_path):
    """
    Extract a zip file
    :param zip_path: The path of the zip file to extract
    :param output_path: The path where the zip file will be extracted

    :return: None
    """
    try:
        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_path)
    except Exception as e:
        logging.error("An error occured while extracting the zip file: %r", e)

def removeFileOrFolder(path):
    """
    Remove a file or a folder
    :param path: The path of the file or folder to remove

    :return: None
    """
    try:
        if Path(path).exists():
            if Path(path).is_file():
                Path(path).unlink()
            elif Path(path).is_dir():
                shutil.rmtree(path)
    except Exception as e:
        logging.error("An error occured while removing %s: %r", path, e)

def cleanUp(output_path):
    """
    Clean up the output folder
    :param output_path: The path of the output folder

    :return: None
    """
    # Move the contents of overrides folder (if it exists) to the output folder
    logging.debug("Moving the contents of overrides folder to the output folder")
    overrides_path = path_join(output_path, "overrides")
    try:
        for item in Path(overrides_path).glob("*"):
            shutil.move(str(item), output_path)
        removeFileOrFolder(overrides_path)
    except Exception as e:
        logging.error("An error occured while moving the contents of overrides folder: %r", e)
    logging.debug("Contents of overrides folder moved successfully")

    # Remove the modlist.html file (if it exists)
    logging.debug("Removing the modlist.html file")
    removeFileOrFolder(path_join(output_path, "modlist.html"))

    # Remove the manifest.json file
    logging.debug("Removing the manifest.json file")
    removeFileOrFolder(path_join(output_path, "manifest.json"))


def downloadMod(projectID, fileID, output_path):
    """
    Download a mod from CurseForge
    :param projectID: The project ID of the mod
    :param fileID: The file ID of the mod
    :param output_path: The path where the mod will be downloaded

    :return: None
    """
    url = BASE_URL.format(projectID=projectID, fileID=fileID)
    download_url = url + "/download"

    # Create an opener that can handle redirects
    opener = build_opener(HTTPRedirectHandler())
    request = Request(download_url)
    response = opener.open(request)

    # After redirects, get the final URL
    final_url = response.geturl()

    # Extract the filename from the final URL or the Content-Disposition header
    filename = basename(urlsplit(final_url).path)  # Default to URL's basename
    content_disposition = response.headers.get('Content-Disposition')
    if content_disposition:
        filename = content_disposition.split('filename=')[-1].strip('"')

    # Log the filename
    logging.info("Downloading %s", filename)

    # Download the file and write to disk
    with open(path_join(output_path, filename), 'wb') as out_file:
        out_file.write(response.read())

    logging.debug("Downloaded %s", filename)

def main(curseforge_zip_path: str, output_path: str):
    # Check if the output path ends with a slash
    if not output_path.endswith("/"):
        output_path += "/"

    # If the target output folder does not exist, create it
    logging.debug("Creating the output folder")
    makedirs(output_path, exist_ok=True)
    logging.debug("Output folder created successfully")

    # Extract the CurseForge modpack zip file to the output folder
    logging.debug("Extracting the CurseForge modpack zip file")
    extractZip(curseforge_zip_path, output_path)
    logging.debug("CurseForge modpack zip file extracted successfully")

    # Read the manifest.json file
    logging.debug("Reading the manifest.json file")
    manifest_path = path_join(output_path, "manifest.json")
    manifest = json_loads(open(manifest_path).read())
    logging.debug("Manifest file read successfully")
    logging.info("Successfully loaded %s version %s", manifest["name"], manifest["version"])

    # Create a mods folder in the output folder
    logging.debug("Creating the mods folder")
    makedirs(path_join(output_path, "mods"), exist_ok=True)
    logging.debug("Mods folder created successfully")

    # Download the mods
    nb_mods_manifest = len(manifest["files"])
    nb_mods_downloaded = 0
    logging.debug("Downloading the mods")
    for mod in manifest["files"]:
        try:
            logging.debug("Downloading mod: %s - %s", mod["projectID"], mod["fileID"])
            downloadMod(mod["projectID"], mod["fileID"], path_join(output_path, "mods"))
            nb_mods_downloaded += 1
        except Exception as e:
            logging.error("An error occured while downloading mod %s - %s: %r", mod["projectID"], mod["fileID"], e)

    if nb_mods_downloaded != nb_mods_manifest:
        logging.warning("Some mods were not downloaded")
        logging.warning("Downloaded %d mods out of %d", nb_mods_downloaded, nb_mods_manifest)
    else:
        logging.info("Downloaded %d mods out of %d", nb_mods_downloaded, nb_mods_manifest)
        # Clean up the output folder
        cleanUp(output_path)
        print("Process completed successfully, you can now use move the content of " + output_path + " folder to your minecraft folder")
        print("Don't forget to install the correct modloader which is : " + manifest["minecraft"]["modLoaders"][0]["id"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) != 3:
        print("Usage: " + sys.argv[0] + " <curseforge_zip_path> <output_path>", file=sys.stderr)
        sys.exit(1)

    curseforge_zip_path = sys.argv[1]
    output_path = sys.argv[2]

    main(curseforge_zip_path, output_path)