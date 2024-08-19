# Curseforge minecraft modpack dowloader

## Usage
- Run the executable with the following command:
```bash
./cfmd <path_to_modpack_zip> <path_to_output_folder>
```
Example:
```bash
./cfmd ~/Downloads/RLCraft.zip ~/Downloads/RLCraft
```

- The modpack will be extracted to the output folder. Then you need to copy the contents of the output folder to your Minecraft instance folder.

## Building
- Install the requirements:
```bash
pip install -r requirements.txt
```

- Run the build script:
```bash
./build.sh
```

- The executable will be in the `dist` folder.
