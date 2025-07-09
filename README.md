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
   git clone [https://github.com/typiconman/AstroEasterPy](https://github.com/typiconman/AstroEasterPy)
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

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 📧 Contact

For any questions or feedback, please open an issue on GitHub.
