# Image Processing Automation Scripts

A collection of Python scripts for automated image processing using OCR (Optical Character Recognition) and QR code detection. These scripts are designed to process large batches of images with different automation tasks.

## Features

- **OCR Text Extraction**: Extract text from images using Tesseract OCR
- **QR Code Detection**: Read and decode QR codes from images
- **Batch Processing**: Process multiple images in parallel for improved performance
- **Progress Tracking**: Visual progress bars for monitoring processing status
- **Error Handling**: Comprehensive error logging and handling
- **File Organization**: Automatic file renaming and organization based on extracted data

## Scripts Overview

### 1. ors_end.py
Processes images in "Errores" folders to extract text and rename files based on specific patterns (WVU/WNE codes).

**Features:**
- Extracts text from PNG images using Tesseract OCR
- Searches for WVU or WNE patterns followed by 12 characters
- Renames files based on extracted patterns
- Handles errors and creates detailed logs

### 2. Qr_end (1).py
Processes images in "De control" folders to read QR codes and rename files accordingly.

**Features:**
- Crops specific regions of images for QR code detection
- Uses ZXing library for QR code reading
- Renames files based on QR code content
- Multi-threaded processing for better performance

### 3. Decontrol_end (1).py
Filters images containing "DE CONTROL" text and organizes them into specific folders.

**Features:**
- OCR text extraction to identify control documents
- Moves matching images to "Constancias" folder
- Creates detailed processing logs
- Multi-process execution for faster processing

## Prerequisites

### Software Requirements
- Python 3.7 or higher
- Tesseract OCR engine

### Tesseract Installation
1. Download and install Tesseract OCR from: https://github.com/tesseract-ocr/tesseract
2. Make sure to install the Spanish language pack if processing Spanish text
3. Update the `pytesseract.tesseract_cmd` path in the scripts to match your installation

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/image-processing-automation.git
cd image-processing-automation
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

3. Update the folder paths in each script to match your directory structure:
   - Update `carpeta_principal` variables in each script
   - Verify Tesseract installation path

## Usage

### Running the Scripts

1. **For OCR text extraction and pattern matching:**
```bash
python ors_end.py
```

2. **For QR code processing:**
```bash
python "Qr_end (1).py"
```

3. **For control document filtering:**
```bash
python "Decontrol_end (1).py"
```

### Directory Structure Expected

```
Main Folder/
├── Subfolder1/
│   └── Errores/          # For ors_end.py
│       ├── image1.png
│       └── image2.png
├── Subfolder2/
│   └── De control/       # For Qr_end (1).py
│       ├── image1.png
│       └── image2.png
└── Documents/            # For Decontrol_end (1).py
    ├── image1.png
    └── image2.png
```

## Configuration

### Customizing Processing Parameters

1. **OCR Language**: Change the `lang` parameter in pytesseract calls
2. **QR Code Region**: Modify crop coordinates in `Qr_end (1).py`
3. **Search Patterns**: Update regex patterns in `ors_end.py`
4. **File Extensions**: Modify file extension filters as needed

### Performance Settings

- **Process Count**: Scripts automatically use available CPU cores
- **Thread Count**: QR processing uses 5 threads by default (configurable)

## Output Files

Each script generates several log files:
- `errores.txt`: General processing errors
- `movimientos.txt`: File movement operations
- `detalles_con_control.txt`: Details of processed control documents
- Individual `.txt` files containing extracted text for each image

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

1. **Tesseract not found**: Ensure Tesseract is properly installed and the path is correct
2. **Permission errors**: Run with appropriate file system permissions
3. **Memory issues**: Reduce the number of parallel processes for large images
4. **QR code not detected**: Verify crop coordinates match your image format

### Support

For issues and questions, please create an issue in the GitHub repository.