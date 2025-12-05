# Fleet Vessels Module

## Description

This module extends the standard Odoo Fleet module to add support for managing vessels (ships, boats, yachts, etc.) as part of your fleet.

## Features

### Vessel Type Support
- Adds "Vessel" as a new vehicle type alongside Car and Bike
- Seamlessly integrates with existing Fleet functionality

### Vessel-Specific Fields

#### Dimensions
- **Length**: Overall length of the vessel
- **Beam**: Width at the widest point
- **Draft**: Vertical distance from waterline to hull bottom
- **Tonnage**: Gross tonnage or displacement
- Configurable units (meters/feet for length, various tonnage units)

#### Maritime Identification
- **IMO Number**: International Maritime Organization unique identifier
- **MMSI**: Maritime Mobile Service Identity (9-digit AIS number)
- **Call Sign**: Radio call sign
- **Flag State**: Country of registration

#### Classification
- **Vessel Type**: Cargo Ship, Passenger Ship, Fishing Vessel, Yacht, Tanker, Container Ship, Naval/Military, Tugboat, Ferry, Research Vessel
- **Hull Material**: Steel, Aluminum, Fiberglass, Wood, Composite, Concrete
- **Propulsion Type**: Diesel, Gasoline, Electric, Hybrid, Sail, Nuclear

#### Performance & Capacity
- **Max Speed**: Maximum speed in knots
- **Passenger Capacity**: Maximum number of passengers
- **Crew Capacity**: Required or maximum crew members

### Vessel Categories

Pre-configured categories include:
- Yacht
- Cargo Ship
- Fishing Vessel
- Passenger Ship
- Tanker
- Container Ship
- Tugboat
- Ferry
- Naval/Military
- Research Vessel

### User Interface

- **Dedicated Vessel Information Tab**: All vessel-specific fields are organized in a separate tab that only appears when the vehicle type is "Vessel"
- **Smart Field Visibility**: Car/bike-specific fields (doors, seats, trailer hitch) are automatically hidden for vessels
- **Search & Filters**: Filter vehicles by vessel type, flag state, and other vessel-specific criteria
- **Kanban View**: Displays IMO number and vessel type in the kanban cards for vessels

## Installation

1. Copy the `fleet_vessels` folder to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the "Fleet Vessels" module

## Dependencies

- `fleet` (Odoo standard Fleet module)

## Demo Data

The module includes demo data with:
- 3 vessel brands (Azimut Yachts, Maersk, Sunseeker)
- 3 vessel models (luxury yachts and container ship)
- 3 vessel instances with complete information

## Usage

### Creating a Vessel Model

1. Go to Fleet → Configuration → Models
2. Create a new model
3. Select "Vessel" as the Vehicle Type
4. Fill in the vessel-specific information in the "Vessel Information" tab
5. Save

### Creating a Vessel

1. Go to Fleet → Fleet → Vehicles
2. Create a new vehicle
3. Select a vessel model
4. The vessel information will be automatically populated from the model
5. You can override any field for this specific vessel
6. Add maritime identification numbers (IMO, MMSI, Call Sign)
7. Save

### Filtering Vessels

- Use the "Vessels" filter in the search bar to show only vessels
- Group by Vessel Type, Flag State, or Hull Material
- Search by IMO number, MMSI, or Call Sign

## Technical Details

### Models Extended

- `fleet.vehicle.model`: Adds vessel-specific fields and extends vehicle_type selection
- `fleet.vehicle`: Adds vessel-specific fields with compute methods from model

### Views Extended

- Vehicle Model Form, Tree, and Search views
- Vehicle Form, Tree, Kanban, and Search views

### Data Files

- `fleet_vessel_categories.xml`: Vessel category definitions
- `fleet_vessel_demo.xml`: Demo data (optional)

## License

LGPL-3

## Author

Custom Odoo Module

## Version

1.0
