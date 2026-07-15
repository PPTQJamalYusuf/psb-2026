import os
import json
import pandas as pd
from collections import Counter

base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "assets", "Formulir Pendaftaran TP 2025_2026 Pusat Pendidikan Tahfidzul Qur'an Jamal Yusuf Al Haddad (Jawaban).xlsx")

# Load data from Excel
df = pd.read_excel(file_path)

# Handle NaNs
df = df.fillna('')

jenjang_counter = Counter()
provinsi_counter = Counter()
gol_darah_counter = Counter()

registrants = []

for _, row in df.iterrows():
    waktu = str(row['Timestamp'])
    if waktu.endswith('00:00:00'): waktu = waktu.replace(' 00:00:00', '')
    
    nama = str(row['NAMA LENGKAP']).strip().title()
    jenjang_raw = str(row['JENJANG PENDIDIKAN\nPilih salah satu !']).strip()
    gol_darah = str(row['GOLONGAN DARAH']).strip()
    provinsi = str(row['PROVINSI']).strip()
    
    # Normalisasi nama provinsi
    prov_lower = provinsi.lower()
    if 'mesuji' in prov_lower and 'lampung' in prov_lower:
        provinsi = 'Lampung'
    elif prov_lower == 'sumatra selatan':
        provinsi = 'Sumatera Selatan'
        
    asal_sekolah = str(row['ASAL SEKOLAH SEBELUMNYA']).strip().title()
    
    if not nama and not jenjang_raw:
        continue
        
    jenjang_clean = jenjang_raw.replace('SETARA ', '').replace(' (PAKET B)', '').replace(' (PAKET C)', '')
    
    status = "Aktif"
    nama_lower = nama.lower()
    if 'ghaziyah afifah' in nama_lower or 'aqilla zahratun' in nama_lower or 'marisa amrin' in nama_lower:
        status = "Mengundurkan Diri"
        
    if status == "Aktif":
        jenjang_counter[jenjang_clean] += 1
        
        if provinsi:
            provinsi_counter[provinsi.title()] += 1
            
        if gol_darah:
            gol_darah_counter[gol_darah] += 1
    
    # Format time for display (just date part if it's too long)
    if ' ' in waktu:
        waktu = waktu.split(' ')[0]
    
    registrants.append({
        'waktu': waktu,
        'nama': nama,
        'jenjang': jenjang_clean,
        'provinsi': provinsi.title(),
        'gol_darah': gol_darah,
        'asal_sekolah': asal_sekolah,
        'status': status
    })

total_pendaftar = sum(1 for r in registrants if r['status'] == 'Aktif')
paket_b = jenjang_counter.get('SMP', 0)
paket_c = jenjang_counter.get('SMA', 0)
top_provinsi = provinsi_counter.most_common(1)[0][0] if provinsi_counter else "-"

# For charts
top_5_provinsi = dict(provinsi_counter.most_common(5))
prov_labels = list(top_5_provinsi.keys())
prov_data = list(top_5_provinsi.values())

jenjang_labels = list(jenjang_counter.keys())
jenjang_data = list(jenjang_counter.values())

html_content = f"""
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Ringkasan Eksekutif PSB 2026</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --primary: #0f172a;      /* Slate 900 */
            --primary-light: #334155; /* Slate 700 */
            --accent: #2563eb;       /* Blue 600 */
            --accent-light: #eff6ff; /* Blue 50 */
            --success: #16a34a;      /* Green 600 */
            --success-light: #f0fdf4;/* Green 50 */
            --bg-body: #f8fafc;      /* Slate 50 */
            --card-bg: #ffffff;
            --text-main: #1e293b;    /* Slate 800 */
            --text-muted: #64748b;   /* Slate 500 */
            --border: #e2e8f0;       /* Slate 200 */
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Poppins', sans-serif;
        }}

        body {{
            background-color: var(--bg-body);
            color: var(--text-main);
            min-height: 100vh;
        }}

        /* Navbar / Header */
        header {{
            background-color: var(--card-bg);
            border-bottom: 1px solid var(--border);
            padding: 1rem 2rem;
            position: sticky;
            top: 0;
            z-index: 50;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .brand img {{
            height: 48px;
            width: auto;
        }}

        .brand-text h1 {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--primary);
            letter-spacing: -0.5px;
        }}

        .brand-text p {{
            font-size: 0.85rem;
            color: var(--text-muted);
            font-weight: 500;
        }}

        .header-actions {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .badge-academic-year {{
            background: var(--accent-light);
            color: var(--accent);
            padding: 0.5rem 1rem;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        /* Main Container */
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
            animation: fadeIn 0.6s ease-out;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .page-title {{
            margin-bottom: 2rem;
        }}

        .page-title h2 {{
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--primary);
        }}
        
        .page-title p {{
            color: var(--text-muted);
            margin-top: 0.25rem;
        }}

        /* Metrics Grid */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .metric-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .metric-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
        }}

        .metric-info h3 {{
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
            font-weight: 600;
        }}

        .metric-info .value {{
            font-size: 2.25rem;
            font-weight: 700;
            color: var(--primary);
            line-height: 1;
        }}
        
        .metric-info .sub-text {{
            font-size: 0.85rem;
            color: var(--success);
            margin-top: 0.5rem;
            font-weight: 500;
        }}

        .metric-icon {{
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
        }}

        .icon-blue {{ background: var(--accent-light); color: var(--accent); }}
        .icon-green {{ background: var(--success-light); color: var(--success); }}
        .icon-slate {{ background: #f1f5f9; color: var(--text-muted); }}

        /* Charts Section */
        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        @media (max-width: 900px) {{
            .charts-grid {{ grid-template-columns: 1fr; }}
        }}

        .chart-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
        }}

        .chart-card h3 {{
            font-size: 1.1rem;
            color: var(--primary);
            margin-bottom: 1.5rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .canvas-container {{
            position: relative;
            height: 300px;
            width: 100%;
        }}

        /* Table Section */
        .table-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
            overflow: hidden;
            margin-bottom: 3rem;
        }}

        .table-header {{
            padding: 1.5rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .table-header h3 {{
            font-size: 1.1rem;
            color: var(--primary);
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .table-container {{
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}

        th, td {{
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--border);
        }}

        th {{
            background-color: #f8fafc;
            color: var(--text-muted);
            font-weight: 600;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            white-space: nowrap;
        }}

        td {{
            font-size: 0.9rem;
            color: var(--text-main);
            vertical-align: middle;
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        tr:hover td {{
            background-color: #f8fafc;
        }}

        .cell-name {{
            font-weight: 600;
            color: var(--primary);
        }}
        
        .cell-time {{
            color: var(--text-muted);
            font-size: 0.85rem;
        }}

        .badge-smp {{
            background-color: #e0e7ff;
            color: #4338ca;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
            white-space: nowrap;
        }}
        
        .badge-sma {{
            background-color: #fce7f3;
            color: #be185d;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
            white-space: nowrap;
        }}

        @media (max-width: 768px) {{
            header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 1rem;
                padding: 1rem;
                position: relative;
            }}
            .container {{
                padding: 1rem;
            }}
            .brand img {{
                height: 36px;
            }}
            .brand-text h1 {{
                font-size: 1.1rem;
            }}
            .page-title h2 {{
                font-size: 1.4rem;
            }}
            .metrics-grid {{
                grid-template-columns: 1fr;
                gap: 1rem;
            }}
            .table-header {{
                padding: 1rem;
            }}
            th, td {{
                padding: 0.75rem 1rem;
            }}
        }}

        footer {{
            text-align: center;
            color: var(--text-muted);
            padding-bottom: 2rem;
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>

    <header>
        <div class="brand">
            <img src="assets/logo.png" alt="Logo PSB" onerror="this.src='https://via.placeholder.com/48?text=Logo'">
            <div class="brand-text">
                <h1>Sistem Informasi PSB</h1>
                <p>Pusat Pendidikan Tahfidzul Qur'an Jamal Yusuf Al Haddad</p>
            </div>
        </div>
        <div class="header-actions">
            <div class="badge-academic-year">
                <i class="fa-regular fa-calendar-check"></i> Tahun Ajaran 2025/2026
            </div>
        </div>
    </header>

    <div class="container">
        <div class="page-title">
            <h2>Bismillah</h2>
            <p>Berikut laporan singkat PSB Tahun 2026</p>
        </div>

        <!-- Top Metrics -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-info">
                    <h3>Total Pendaftar Masuk</h3>
                    <div class="value">{total_pendaftar}</div>
                    <div class="sub-text"><i class="fa-solid fa-arrow-trend-up"></i> Calon Santri Aktif</div>
                </div>
                <div class="metric-icon icon-blue"><i class="fa-solid fa-users"></i></div>
            </div>
            
            <div class="metric-card">
                <div class="metric-info">
                    <h3>Pendaftar Jenjang SMP</h3>
                    <div class="value">{paket_b}</div>
                </div>
                <div class="metric-icon icon-slate"><i class="fa-solid fa-book-open-reader"></i></div>
            </div>
            
            <div class="metric-card">
                <div class="metric-info">
                    <h3>Pendaftar Jenjang SMA</h3>
                    <div class="value">{paket_c}</div>
                </div>
                <div class="metric-icon icon-slate"><i class="fa-solid fa-graduation-cap"></i></div>
            </div>
            
            <div class="metric-card">
                <div class="metric-info">
                    <h3>Provinsi Dominan</h3>
                    <div class="value" style="font-size: 1.5rem; margin-top: 10px; margin-bottom: 5px;">{top_provinsi}</div>
                    <div class="sub-text" style="color: var(--text-muted);">Wilayah Asal Terbanyak</div>
                </div>
                <div class="metric-icon icon-green"><i class="fa-solid fa-map-location-dot"></i></div>
            </div>
        </div>

        <!-- Charts Row -->
        <div class="charts-grid">
            <div class="chart-card">
                <h3><i class="fa-solid fa-chart-pie" style="color: var(--accent);"></i> Komposisi Jenjang Pendidikan</h3>
                <div class="canvas-container">
                    <canvas id="jenjangChart"></canvas>
                </div>
            </div>
            
            <div class="chart-card">
                <h3><i class="fa-solid fa-chart-bar" style="color: var(--accent);"></i> Sebaran 5 Provinsi Asal Terbanyak</h3>
                <div class="canvas-container">
                    <canvas id="provinsiChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Data Table -->
        <div class="table-card">
            <div class="table-header">
                <h3><i class="fa-solid fa-table-list" style="color: var(--accent);"></i> Rekapitulasi Rinci Data Calon Santri Baru</h3>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th width="5%">No.</th>
                            <th width="15%">Waktu Registrasi</th>
                            <th width="25%">Nama Calon Santri</th>
                            <th width="20%">Asal Sekolah</th>
                            <th width="10%">Gol. Darah</th>
                            <th width="10%">Jenjang</th>
                            <th width="15%">Provinsi Asal</th>
                        </tr>
                    </thead>
                    <tbody>
"""

for i, reg in enumerate(registrants, 1):
    jenjang_badge_class = "badge-sma" if "SMA" in reg['jenjang'] else "badge-smp"
    
    # Styling for withdrawn
    row_style = "opacity: 0.6; background-color: #f8fafc;" if reg['status'] == 'Mengundurkan Diri' else ""
    nama_display = f"<del>{reg['nama']}</del> <span style='color: #ef4444; font-size: 0.75rem; font-weight: 600; margin-left: 8px;'>(Mundur)</span>" if reg['status'] == 'Mengundurkan Diri' else reg['nama']
    
    html_content += f"""
                        <tr style="{row_style}">
                            <td style="color: var(--text-muted); font-weight: 500;">{i}</td>
                            <td class="cell-time">{reg['waktu']}</td>
                            <td class="cell-name">{nama_display}</td>
                            <td style="font-size: 0.85rem; color: var(--text-muted);">{reg['asal_sekolah']}</td>
                            <td>{reg['gol_darah'] if reg['gol_darah'] else '-'}</td>
                            <td><span class="{jenjang_badge_class}">{reg['jenjang']}</span></td>
                            <td>{reg['provinsi']}</td>
                        </tr>
"""

html_content += f"""
                    </tbody>
                </table>
            </div>
        </div>
        
    </div>

    <footer>
        &copy; 2026 Hak Cipta Panitia PSB TP 2025/2026 &middot; Dibuat secara otomatis untuk kebutuhan Ringkasan Eksekutif.
    </footer>

    <script>
        // Set defaults for Chart.js
        Chart.defaults.font.family = "'Poppins', sans-serif";
        Chart.defaults.color = "#64748b";

        // Jenjang Chart (Doughnut)
        const ctxJenjang = document.getElementById('jenjangChart').getContext('2d');
        new Chart(ctxJenjang, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(jenjang_labels)},
                datasets: [{{
                    data: {json.dumps(jenjang_data)},
                    backgroundColor: ['#4338ca', '#be185d'],
                    borderWidth: 0,
                    hoverOffset: 4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {{
                    legend: {{ position: 'bottom', labels: {{ padding: 20, usePointStyle: true }} }}
                }}
            }}
        }});

        // Provinsi Chart (Bar)
        const ctxProvinsi = document.getElementById('provinsiChart').getContext('2d');
        new Chart(ctxProvinsi, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(prov_labels)},
                datasets: [{{
                    label: 'Jumlah Pendaftar',
                    data: {json.dumps(prov_data)},
                    backgroundColor: '#3b82f6',
                    borderRadius: 6,
                    barThickness: 30
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        grid: {{ color: '#f1f5f9' }},
                        border: {{ display: false }},
                        ticks: {{ precision: 0 }}
                    }},
                    x: {{
                        grid: {{ display: false }},
                        border: {{ display: false }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

output_path = os.path.join(base_dir, "index.html")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Laporan Dashboard Eksekutif berhasil dibuat di {output_path}")
