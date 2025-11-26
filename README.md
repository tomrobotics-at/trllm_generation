# LLM Generated Images Project

This project generates synthetic images with various traffic scenarios using Google's Gemini API for image editing and generation. The tool is designed to create balanced datasets by generating images with different object distributions (pedestrians, bicycles, trucks, buses, motorcycles, and cars).

## Project Structure

```
.
├── README.md
├── requirements.txt
├── run.py                          # Main script for image generation
├── background_images/              # Source background images
│   ├── CAM1.png
│   ├── CAM2.png
│   ├── CAM3.png
│   └── CAM4.png
├── generated_Images/               # Previously generated images and annotations
│   ├── CAM1/
│   │   ├── annotations.json
│   │   ├── images/
│   │   └── sampled_predictions/
│   ├── CAM2/
│   ├── CAM3/
│   └── CAM4/
└── output/                         # New generated images output
    ├── CAM1_new_prompt/
    ├── CAM2_new_prompt/
    ├── CAM3_new_prompt/
    ├── CAM4_new_prompt/
    └── old_prompt/
```

## Features

- **Balanced Dataset Generation**: Creates scenarios to balance object distribution across different traffic scene types
- **Multiple Scenarios**: Generates images with different emphases:
  - `bicycle_heavy` (30% of images) - Boost bicycle presence
  - `pedestrian_heavy` (25% of images) - Boost pedestrian presence  
  - `truck_bus_heavy` (20% of images) - Boost trucks and buses
  - `motorcycle_heavy` (15% of images) - Boost motorcycles
  - `mixed_balanced` (10% of images) - Mixed scenes with minimal cars

- **Customizable Generation**: Configure input images, output folders, and number of images to generate
- **Rate Limiting**: Built-in delays between API requests to respect rate limits

## Setup

### Prerequisites

1. **Google AI Studio API Key**: Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. **Python Dependencies**: Install required packages

### Installation

1. Clone or download this project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your API key as an environment variable:
   ```bash
   export API_KEY="your_actual_api_key_here"
   ```

## Usage

### Basic Usage

Generate 200 images using the default CAM2 background:

```bash
python run.py
```

### Advanced Usage

```bash
python run.py --input_image background_images/CAM1.png \
              --dest_folder output/CAM1_custom/images \
              --num_images 100
```

### Command Line Arguments

- `--input_image`, `-i`: Path to input background image (default: `background_images/CAM2.png`)
- `--dest_folder`, `-d`: Destination folder for generated images (default: `output/CAM2_new_prompt/images`)  
- `--num_images`, `-n`: Number of images to generate (default: 200)

## Output

Generated images are saved with descriptive filenames that include:
- Scenario type (e.g., `bicycle_heavy`, `pedestrian_heavy`)
- Image number in sequence
- Random identifier
- Object counts in the console output

Example output filename: `generated_CAM2_bicycle_heavy_15_abc123.png`

## Current Dataset Distribution

The tool is designed to balance the following object distribution:
- Car: 72.07% → Reduced in generated images
- Pedestrian: 15.5% → Boosted significantly  
- Bicycle: 4.57% → Boosted significantly
- Truck: 3.18% → Boosted moderately
- Motorcycle: 2.45% → Boosted moderately
- Bus: 2.23% → Boosted moderately

## API Information

This project uses Google's Gemini 2.5 Flash Image Preview model for image generation and editing. Make sure you have sufficient API credits and respect rate limits.

## Security Note

Store your API key as an environment variable rather than hardcoding it in the script for security purposes.