# Streamlit Random Racetrack Generator

**Try the live demo:** https://acestudio-racetrack-generator.streamlit.app/

A sophisticated Streamlit application for generating random horse racing racetracks with detailed environmental simulations, satellite HUD maps, and narrative commentary.

## Project Overview

The Random Racetrack Generator is an interactive web application that creates randomized horse racing events with realistic environmental conditions, geographic locations, and detailed narratives. Built with Streamlit, the application simulates various aspects of horse racing including track conditions, weather, time of day, and generates immersive commentary for each race.

Users can generate race packs with different configurations, manually allocate races to slots using a "Race Director" mode, and visualize race locations on interactive maps with satellite HUD overlays.

## Architecture & File Structure

```
random_racetrack_generator/
│
├── app.py                    # Main Streamlit application
├── racetrack.csv             # Primary data source containing race information (~6,000+ horse racing events)
├── user_groups.json          # Persistent storage for user-created race libraries
│
├── Assets:
│   ├── bell_chime.wav        # Sound effect for race generation
│   ├── dirt_bg.png           # Background image for dirt tracks
│   ├── fanfare.wav           # Sound effect for race completion
│   ├── g1_satellite_icon.png # Satellite icon for G1 races
│   ├── g2_satellite_icon.png # Satellite icon for G2 races
│   ├── g3_satellite_icon.png # Satellite icon for G3 races
│   ├── local_satellite_icon.png # Satellite icon for local races
│   ├── non_graded_satellite_icon.png # Satellite icon for non-graded races
│   ├── racetrack_bg.png      # Main background image
│   └── turf_bg.png           # Background image for turf/synthetic tracks
│
├── .kilo/                    # Kilo AI configuration directory
├── .kilocode/                # Legacy Kilo configuration
├── venv/                     # Python virtual environment
└── __pycache__/              # Python bytecode cache
```

### Core Components

- **app.py**: The main application containing all Streamlit logic, data processing functions, UI components, and visualization routines
- **racetrack.csv**: CSV database with ~6,000+ horse racing events containing fields like:
  - racetrack, country, continent, length, length_type, track_type
  - race_name, organizer, race_rank, race_type, race_special
  - latitude, longitude (for geographic visualization)
- **user_groups.json**: JSON file storing user-created race libraries and groupings

## Technical Specifications

### Environmental Simulation Engine

The application features a sophisticated cascading probability simulation system that determines race conditions based on:

1. **Track Wear**: Fresh (50%), Used (35%), Worn (15%)
2. **Weather**: Fair (60%), Cloudy (20%), Rainy (15%), Snowy (5%) - with seasonal adjustments
3. **Temperature**: Hot (Summer/Tropical + Fair), Cold (Winter or high latitude + Rainy/Snowy), Normal (otherwise)
4. **Ground Condition**: Determined by weather and track wear combinations

### Geographic Coordinate System

- Uses real latitude/longitude coordinates from the racetrack dataset
- Implements both 3D tactical globe and Satellite HUD map visualizations
- Features animated radar rings, satellite icon overlays, and HUD data displays

### Narrative Generation Engine

Features a modular narrative system with 9 layers:
1. Umamusume Tactical Layer (track-specific hints)
2. Umamusume Character Resonance (horse personality types)
3. Elite Track Tactical Hooks (high-fidelity track-specific)
4. Special Event Logic (Breeders' Cup and special series)
5. Continental Atmospheric Modules
6. Country-Specific Tactical Hooks
7. Enhanced Time-of-Day Environmental
8. Extreme Regional Weather
9. Library Hooks (series and collection context)

### Algorithmic Features

- **Geographic Anchor Stickiness**: Smart filling logic that prefers races from the same country/continent
- **Prestige Ladder Logic**: Automatic rank progression based on slot positioning
- **Country Diversity Mode**: Option to force different countries in generated packs
- **Dynamic Environment Simulation**: Real-time calculation of season, weather, temperature, and ground conditions

## Function Documentation

### Main Application Functions

#### Data Loading & Caching
- `load_data(file, mtime=None)`: Loads and caches CSV data with memoization
- `get_country_flag(country_name)`: Returns flag image HTML for a country
- `get_country_flag_emoji(country_name)`: Returns flag emoji for a country

#### Environmental Simulation
- `get_season_for_hemisphere(month, lat)`: Determines season based on latitude and month
- `get_time_of_day(hour)`: Converts hour to time of day (Midday, Evening, Night)
- `simulate_race_environment(lat, season, time_of_day)`: Core cascading probability simulation
- `get_skill_tags(row, env)`: Generates skill tags based on race data and environment

#### UI Rendering Functions
- `get_card_bg(rank)`: Returns CSS class for race card background based on rank
- `get_rank_badge(rank, is_major)`: Returns HTML badge for race rank
- `get_track_badge(track_type)`: Returns HTML badge for track type
- `render_card_html(row, is_selected=False, is_active=False)`: Generates HTML for race cards
- `render_full_detail_card(row_data, env=None)`: Generates detailed race information display
- `render_pending_card()`: Returns placeholder HTML for loading states

#### Map Visualization
- `get_satellite_config_by_rank(race_rank)`: Returns satellite icon and ring color based on rank
- `render_satellite_hud_map(highlighted_rows, selected_idx)`: Creates Satellite HUD map visualization
- `render_map(highlighted_rows, selected_idx=0)`: Creates 3D tactical globe visualization
- `display_map_with_hud(placeholder, highlighted_rows, selected_idx)`: Helper to render map + HUD overlays

#### Narrative Generation
- `get_narrative_layer(layer_type, key, default="")`: Retrieves narrative text from modular layers
- Narrative assembly system that combines multiple layers for rich storytelling

#### Data Management
- `save_user_groups(groups)`: Saves user groups to JSON file
- `sync_user_groups_with_csv(df, current_groups)`: Dynamically adds missing race groupings from CSV

#### Export & Utilities
- `export_pdf(races_df)`: Exports race data to PDF format
- `format_race_name(name)`: Formats race name for display based on naming conventions

### Session State Variables

The application uses Streamlit's session state to maintain:
- `generated_races`: DataFrame of currently generated races
- `selected_race_idx`: Index of currently selected/focused race
- `race_environments`: Dictionary mapping race indices to their environmental conditions
- `gen_id`: Generation ID used for tracking and animations
- `director_mode`: Boolean indicating if Race Director mode is active
- `director_slots`: List of 5 slots for manual race allocation in Director mode
- `user_groups`: Dictionary of user-created race libraries
- `map_mode`: Selected map visualization mode ("3D Tactical Globe" or "Satellite HUD Map")

## Setup & Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/maitrongnhan2002/streamlit_random_racetrack_generator.git
   cd streamlit_random_racetrack_generator
   ```

2. **Activate the virtual environment** (if you haven't already):
   - If you just cloned the repository and see a `venv/` directory, you can activate it:
     # On Windows:
     venv\Scripts\activate
     # On Unix or MacOS:
     source venv/bin/activate
   - If you don't have a virtual environment, create one first:
     ```bash
     python -m venv venv
     # Then activate as above
     ```

3. **Install dependencies** (if not already installed):
   ```bash
   pip install streamlit pandas plotly fpdf pycountry
   ```

4. **Launch the application**:
   ```bash
   streamlit run app.py
   ```

### Windows Convenience Script (Optional)

For Windows users who want to run `streamlit run app.py` without manually activating the virtual environment each time, you can use the provided batch file:

1. Ensure you are in the project root directory.
2. Run the following command:
   ```
   .\streamlit.bat run app.py
   ```

   This batch file (`streamlit.bat`) automatically activates the virtual environment and runs the Streamlit command with any arguments you provide.

   > **Note**: The `streamlit.bat` file is already included in the repository. If you deleted it, you can recreate it with the following content:
   > ```batch
   > @echo off
   > call venv\Scripts\activate.bat
   > streamlit %*
   > ```

### Dependencies
- streamlit: Web application framework
- pandas: Data manipulation and analysis
- plotly: Interactive visualizations
- fpdf: PDF generation
- pycountry: Country code lookup

## Usage

> **Important**: The `streamlit run app.py` command must be run inside the activated virtual environment. If you see a `ModuleNotFoundError`, make sure the virtual environment is activated.

### Basic Operation

1. Launch the application using `streamlit run app.py` (or use the convenience script on Windows as described above).
2. Use the sidebar controls to:
   - Upload a custom racetrack.csv file (optional)
   - Adjust global filters (continent, country, racecourse, organizer, length type, track type, race rank)
   - Toggle "Different Countries" option for geographic diversity
   - Select generation mode:
     - **Uma 5-Race Pack**: Generates a balanced pack with specific surface/distance distribution
     - **AceStudio 5-Race Pack**: Generates a pack with progressive distance variation
     - **Custom N-Race Pack**: Generates a variable number of races (1-30)
   - Access Race Director mode for manual slot allocation

### Race Director Mode

Enable Race Director mode using the toggle in the sidebar to:
- Manually allocate specific races to 5 slots
- Set manual overrides for rank, weather, ground, and time conditions
- Use smart filling logic to auto-populate empty slots
- Swap races between slots and your stable
- Save races to your personal libraries

### Map Visualization

Choose between two map modes:
- **3D Tactical Globe**: Interactive globe showing race connections with start/finish markers
- **Satellite HUD Map**: Realistic satellite view with animated radar rings, satellite icon overlays, and HUD data displays

### Saving & Managing Races

- Use the "➕" button on generated races to save them to your default library
- Access "The Stable" in the sidebar to manage your race libraries
- Create, rename, delete, and organize libraries
- Pick up races from libraries to use in Director mode slots
- Reorder and remove races within libraries

### Environmental Controls

Use the "Race Environment" expander in the sidebar to:
- Enable/disable auto-detection of current time and month
- Manually set month and hour for custom environmental conditions
- Observe how seasonal and temporal changes affect race simulations

## How It Works

When you generate races:
1. The application filters the race database based on your sidebar selections
2. Depending on the selected mode, it applies specific algorithms to choose races:
   - Standard modes distribute races across surface/type categories
   - Director mode uses anchor/sticky logic for geographic consistency
   - Country diversity mode ensures geographic variety
3. For each selected race, the environmental simulation engine calculates:
   - Current season based on geographic location and date
   - Realistic weather, temperature, track wear, and ground conditions
4. The narrative engine generates immersive commentary by combining:
   - Track-specific tactical hints
   - Environmental atmospheric descriptions
   - Special event context when applicable
   - Time-of-day and regional weather effects
5. Results are displayed with:
   - Visual race cards showing key information
   - Interactive maps with geographic context
   - Detailed panels with environmental data and skill tags
   - Audio effects for user feedback

## Features

- 🎮 **Interactive Interface**: Modern, responsive UI with Streamlit
- 🌍 **Real Geographic Data**: Uses actual latitude/longitude coordinates
- 🌦️ **Dynamic Environmental Simulation**: Realistic weather and track conditions
- 📖 **Rich Narrative Generation**: Multi-layered storytelling system
- 🗺️ **Dual Map Visualization**: 3D globe and Satellite HUD views
- 🏆 **Prestige Ranking System**: G1, G2, G3, Local, and Non-graded classifications
- 💾 **Persistent Libraries**: Save and organize your favorite races
- 🎧 **Audio Feedback**: Sound effects for race generation and completion
- 🖨️ **Export Functionality**: Save results to PDF format
- 🔧 **Race Director Mode**: Advanced manual control and allocation features

---
*Built with Streamlit for interactive data applications*