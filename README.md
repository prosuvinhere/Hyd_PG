# 🏠 Hyd Life: Hyderabad PG Finder & Market Intelligence

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B.svg)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-6366f1.svg)
![Status](https://img.shields.io/badge/Status-Live-success)

**Hyd Life** is a real-time, community-driven PG & Co-Living discovery and market intelligence dashboard for Hyderabad. Built in collaboration with the **r/hyderabad** community, it connects directly to a live crowdsourced Google Sheet (with offline local CSV fallback), performs automated ETL data cleaning, extracts smart review tags, scores accommodations by value-for-money, and maps proximity to Hyderabad Metro lines and major IT hubs.

---

## 🚀 Key Features

* **📡 Resilient Live Data Pipeline:** Automatically fetches the latest submissions from the public Google Sheet with 10-minute caching, on-demand refresh, and seamless fallback to the local `pg_data.csv` snapshot when offline.
* **🧹 Intelligent ETL & Sanitization:**
  * Fixes messy rent inputs (`₹12,000`, ranges like `5k-6k`, shorthand like `8.5` → `₹8,500`, and extra-zero typos like `120000` → `₹12,000`).
  * Normalizes `Type of PG` (`Male Only`, `Female Only`, `Co-Living`), parking availability, room space, and electricity billing.
  * Cleans and formats 10-digit Indian phone numbers (`+91 XXXXX XXXXX`) with direct **WhatsApp** contact links.
  * Canonicalizes 30+ Hyderabad localities (`Madhapur`, `Gachibowli`, `Kondapur`, `Gowlidoddy`, `HITEC City`, `Kokapet`, `Financial District`, `Kukatpally`, `KPHB`, `Uppal`, `Dilsukhnagar`, `Pocharam`, etc.).
* **🏷️ Smart Tagging Engine:** Scans community reviews and structured fields to surface positive amenity badges (`🚀 Good Wi-Fi`, `🚇 Near Transit/Metro`, `🏋️ Gym`, `❄️ AC`, `🧺 Laundry/Washing`, `🔋 Power Backup`, `🍳 Fridge/Self-Cook`, `🔒 CCTV/Security`, `⚡ Elec. Included`, `🚗 4W Parking`) as well as red-flag warnings (`⚠️ Pest Alert`, `⚠️ Mgmt/Deposit Alert`).
* **💎 Value-for-Money Scoring:** Ranks listings using a custom Value Score formula that rewards high community ratings relative to monthly rent:
  $$\text{Value Score} = \left( \frac{\text{Rating}^2}{\text{Monthly Cost}} \right) \times 5000$$
* **⚖️ Side-by-Side PG Comparison:** Select up to 4 PGs to compare rent, overall rating, food quality, room space, electricity inclusion, nearest metro distance, and full reviews head-to-head.
* **🚇 Interactive Metro & IT Hub Commute Planner:**
  * Interactive Plotly Mapbox visualization plotting every PG alongside **Hyderabad Metro lines (Blue, Red, Green)** and stations.
  * **Office Hub Distance Calculator:** Pick your workplace hub (*Mindspace / HITEC City, DLF Cyber City, Financial District / WaveRock, Knowledge City, Kondapur, Kokapet SEZ, Ameerpet, Pocharam, Adibatla*) to filter and rank PGs within your target commute radius.
* **📊 Rich Market Analytics:** Interactive histograms, sunburst breakdowns, locality rent bar charts, rent variation box plots, price-vs-rating bubble matrices (sized by food quality), and room space violin plots.

---

## 🛠️ Installation & Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/prosuvinhere/Hyd_PG.git
   cd Hyd_PG
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit application**
   ```bash
   streamlit run app.py
   ```

---

## 📄 Data Schema (Google Sheet / `pg_data.csv`)

| Column Name | Description |
| :--- | :--- |
| `Timestamp` | Submission timestamp |
| `Name of PG/Hostel:` | Property name |
| `Type of PG` | `Male Only`, `Female Only`, or `Co Living ( Male & Female both)` |
| `🌍 Location:` | Locality / neighborhood in Hyderabad |
| `🏡Type of Sharing:` | `Single`, `Two Sharing`, `Triple Sharing`, `Four Sharing`, `Five Sharing` |
| `💰 Monthly Cost (₹):` | Monthly rent in INR |
| `🍴 Food Quality:` | 1 to 5 rating for food quality |
| `🚲Parking Space` | 2-Wheeler / 4-Wheeler / No Parking details |
| `🏢 Room Space:` | `Spacious`, `Average`, or `Cramped` |
| `⚡Electricity Bill:` | `Included in rent` or `Separate bill` |
| `Overall Rating:` | 1 to 5 overall rating |
| `Additional Comments:` | Detailed pros, cons, landmarks, and amenities review |
| `Contributor Reddit Username` | Reddit username of reviewer (or `Anonymous`) |
| `PG Owner Phone number` | Direct owner/caretaker contact number |
| `Contributor Gender` | Optional reviewer metadata |

---

## 🤝 Contributing

Contributions and PG review submissions are welcome!
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

<div align="center">
  Built with ❤️ for the <b>r/hyderabad</b> community using Python & Streamlit
</div>
