# 🏠 Hyd Life: PG Finder & Market Intelligence

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)
![Status](https://img.shields.io/badge/Status-Live-success)

**Hyd Life** is a real-time, data-driven dashboard designed to help bachelors find accommodation (PGs/Hostels) in Hyderabad. Unlike static listings, this app connects to a live crowd-sourced Google Sheet, performs ETL (Extract, Transform, Load) operations on the fly, and generates actionable analytics using a custom recommendation engine.

## 🚀 Key Features

* **Live Data Pipeline:** Fetches data directly from a public Google Sheet, ensuring listings are always up-to-date without database maintenance.
* **Smart Tagging Engine:** automatically scans user reviews for keywords (e.g., "fast wifi", "bad food", "metro") and assigns visual emoji tags (🚀, 🥣, 🚇) for quick decision-making.
* **"Value Score" Algorithm:** A custom metric that ranks PGs not just by price, but by value for money using the formula: $(Rating^2 / Cost)$.
* **Geospatial Visualization:** Interactive map plotting approximate PG locations with "Jitter" logic to prevent marker overlap in dense hubs like Gachibowli.
* **Market Analytics:** Interactive Plotly charts visualizing rent distribution, sharing types, and cost-vs-rating matrices.

## 📊 How It Works

### 1. Data Ingestion & Cleaning
The app pulls raw CSV data from Google Sheets. It handles messy real-world data by:
* Standardizing currency inputs (converting `5k-6k` to `5500`).
* Imputing missing ratings and location coordinates.

### 2. The Recommendation Logic
We don't just sort by cheapest price. We calculate a **Value Score**:
$$\text{Value Score} = \left( \frac{\text{Rating}^2}{\text{Monthly Cost}} \right) \times 5000$$
*This prioritizes high-rated stays significantly, even if they cost slightly more, filtering out cheap but poor-quality options.*

### 3. Geolocation
Locations are mapped using a lookup dictionary for Hyderabad's major IT hubs (Gachibowli, Hitec City, Kondapur, etc.). Random noise (Gaussian jitter) is added to coordinates to visualize clusters effectively.

## 🛠️ Installation & Local Setup

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/yourusername/hyd-pg-finder.git](https://github.com/yourusername/hyd-pg-finder.git)
    cd hyd-pg-finder
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application**
    ```bash
    streamlit run app.py
    ```

## 📄 Data Schema (Google Sheet)

To use your own data source, ensure your Google Sheet is **Public (View Only)** and follows this column structure. Update the `sheet_id` and `sheet_gid` in `app.py`.

| Column Name | Description |
| :--- | :--- |
| **Name of PG/Hostel:** | Name of the property |
| **Type of PG** | Gents / Ladies / Co-ed |
| **🌍 Location:** | Area name (e.g., Gachibowli) |
| **🏡Type of Sharing:** | 1, 2, 3, 4 Sharing |
| **💰 Monthly Cost (₹):** | Numeric or Range (e.g., 5000-6000) |
| **Overall Rating:** | 1 to 5 scale |
| **Additional Comments:** | Text reviews for Smart Tagging |
| **PG Owner Phone number** | Contact details |

## 📦 Dependencies

* `streamlit` - Web framework
* `pandas` - Data manipulation
* `numpy` - Mathematical operations
* `plotly` - Interactive visualizations

## 🤝 Contributing

Contributions are welcome!
1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/NewFeature`)
3.  Commit your Changes (`git commit -m 'Add some NewFeature'`)
4.  Push to the Branch (`git push origin feature/NewFeature`)
5.  Open a Pull Request

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---
<div align="center">
  Built with ❤️ in Hyderabad using Python
</div>
