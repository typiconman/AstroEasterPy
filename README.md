# AstroEasterPy

Determine the astronomical date of Easter in Python.

This Python program computes the astronomical date of Easter. Astronomical computations utilize the powerful [Skyfield](https://rhodesmill.org/skyfield/) library.

## 🌟 Methodology

1. For a given year, compute the instant of the vernal equinox in UTC.

2. Compute the instant of the full moon that occurs after the instant of the vernal equinox in UTC.

3. Convert the time of the full moon to local time at the longitude of the Church of the Holy Sepulcher in Jerusalem (`35°13′47.2″ E = 35.2298° E`).

4. Find the first Sunday after this instant. If the full moon occurs on a Sunday, then the next Sunday is used.

## 🚀 Installation

To get started with this project, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/typiconman/AstroEasterPy
   cd AstroEasterPy
   ```

2. **Create a virtual environment (recommended):**

   It's good practice to use a virtual environment to manage project dependencies.

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

    * **On macOS/Linux:**

    ```bash
    source venv/bin/activate
    ```

    * **On Windows:**

    ```bash
    .\venv\Scripts\activate
    ```

4.  **Install dependencies:**

    All required Python packages are listed in the `requirements.txt` file. Install them using pip:
    
    ```bash
    pip install -r requirements.txt
    ```

## 💡 Usage

Once installed, you can run the script from your terminal.

```bash
python easter_calculator.py <year>
```

Replace `<year>` with the desired year for which you want to compute the Easter date.

**Example:**

To find the astronomical Easter date for the year 2025:

```bash
python easter_calculator.py 2025
```

**Limitations:**

For dates between 1549 and 2650, we use the data from Jet Propulsion Laboratory’s (JPL) DE440 ephemeris, provided in the `de440.bsp` file (it will be downloaded the first time you run the program). For dates outside of this range, but between the years 3001 BC and 3000 AD, data from the older JPL DE406 ephemeris are used, provided in the `de406.bsp` file (again, downloaded as needed). Dates outside of this range will result in an error `skyfield.errors.EphemerisRangeError`. Results too far into the future should not be viewed as completely reliable due to uncertainty in [Delta T](https://eclipse.gsfc.nasa.gov/SEcat5/deltat.html).

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 📧 Contact

For any questions or feedback, please open an issue on GitHub.
