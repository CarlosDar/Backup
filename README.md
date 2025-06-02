# CNT-91 Frequency Counter Interface

This Python library provides an interface for controlling and acquiring data from the CNT-91 Frequency Counter instrument via GPIB communication.

## Features

- Frequency measurement in single and continuous modes
- Temperature monitoring
- Allan deviation calculations
- Data acquisition with timestamps
- Data visualization and export to Excel
- Hardware pacing support
- Statistical analysis capabilities

## Requirements

- Python 3.x
- PyVISA
- NumPy
- Pandas
- Matplotlib

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/cnt91-interface.git
cd cnt91-interface
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

Basic example:
```python
import CNT_9X_pendulum as CNT

# Create instrument instance
cnt = CNT.CNT_frequenciometro()

# Single frequency measurement
freq = cnt.measure_frequency('A')
print(f"Frequency: {freq} Hz")

# Continuous measurement with Allan deviation
freqs, timestamps, delta_times, adevs, taus = cnt.medir_n_muestras_equidistantesV7(
    n_muestras=100,
    intervalo_s=0.2,
    graficarFT=True,
    graficarDevTau=True
)
```

## Documentation

The library provides several methods for different measurement scenarios:

- `measure_frequency()`: Single frequency measurement
- `measure_frequency_array_CONTINUOUS()`: Continuous frequency measurement
- `medir_n_muestras_equidistantesV7()`: Advanced measurement with Allan deviation
- `leer_adev_cnt91()`: Read internal Allan deviation
- `Measure_temperature_example()`: Monitor instrument temperature

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Carlos Darvoy Espigulé 