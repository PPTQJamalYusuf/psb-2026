import os
import json
import pandas as pd
from collections import Counter

base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "assets", "Formulir Pendaftaran TP 2025_2026 Pusat Pendidikan Tahfidzul Qur'an Jamal Yusuf Al Haddad (Jawaban).xlsx")

# Load data from Excel
df = pd.read_excel(file_path)
df = df.fillna('')

nama_list = []
tempat_lahir_list = []
alamat_list = []
jenjang_list = []

for _, row in df.iterrows():
    nama = str(row['NAMA LENGKAP']).strip().title()
    jenjang_raw = str(row['JENJANG PENDIDIKAN\nPilih salah satu !']).strip()
    tempat_lahir = str(row['TEMPAT LAHIR']).strip()
    
    alamat_parts = []
    if row['ALAMAT RUMAH']: alamat_parts.append(str(row['ALAMAT RUMAH']))
    if row['DESA/KELURAHAN/KAMPUNG']: alamat_parts.append(str(row['DESA/KELURAHAN/KAMPUNG']))
    if row['KECAMATAN, KABUPATEN/KOTA']: alamat_parts.append(str(row['KECAMATAN, KABUPATEN/KOTA']))
    
    provinsi = str(row['PROVINSI']).strip()
    if provinsi:
        prov_lower = provinsi.lower()
        if 'mesuji' in prov_lower and 'lampung' in prov_lower:
            provinsi = 'Lampung'
        elif prov_lower == 'sumatra selatan':
            provinsi = 'Sumatera Selatan'
        alamat_parts.append(provinsi)
        
    alamat = ", ".join(alamat_parts)
    
    if not nama and not jenjang_raw:
        continue
        
    nama_lower = nama.lower()
    if 'ghaziyah afifah' in nama_lower or 'aqilla zahratun' in nama_lower or 'marisa amrin' in nama_lower:
        continue
        
    nama_list.append(nama)
    tempat_lahir_list.append(tempat_lahir.title())
    alamat_list.append(alamat.title())
    jenjang_list.append(jenjang_raw.replace('SETARA ', '').replace(' (PAKET B)', '').replace(' (PAKET C)', ''))

total_responses = len(nama_list)
jenjang_counts = Counter(jenjang_list)

# Prepare Chart.js data
jenjang_labels = list(jenjang_counts.keys())
jenjang_data = list(jenjang_counts.values())

html_content = f"""
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rangkuman PSB 2026</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-color: #f0f4f8; /* Light blue/gray typical of forms */
            --form-theme: #1a73e8; /* Google Blue */
            --text-dark: #202124;
            --text-gray: #5f6368;
            --border-color: #dadce0;
            --card-bg: #ffffff;
            --response-bg: #f8f9fa;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            background-color: var(--bg-color);
            color: var(--text-dark);
            font-family: 'Poppins', sans-serif;
            line-height: 1.5;
            padding-bottom: 4rem;
        }}

        .container {{
            max-width: 770px;
            margin: 0 auto;
            padding: 1rem;
        }}

        /* Header Card */
        .header-card {{
            background: var(--card-bg);
            border-radius: 8px;
            border: 1px solid var(--border-color);
            border-top: 10px solid var(--form-theme);
            padding: 24px;
            margin-top: 12px;
            margin-bottom: 24px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}

        .header-card .logo {{
            width: auto;
            height: 60px;
            margin-bottom: 16px;
            object-fit: contain;
        }}

        .header-title {{
            font-family: 'Poppins', sans-serif;
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 12px;
            color: var(--text-dark);
        }}

        .header-desc {{
            font-size: 14px;
            color: var(--text-gray);
        }}
        
        .header-total {{
            font-family: 'Poppins', sans-serif;
            font-size: 24px;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid var(--border-color);
        }}

        /* Question Card */
        .question-card {{
            background: var(--card-bg);
            border-radius: 8px;
            border: 1px solid var(--border-color);
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            page-break-inside: avoid;
        }}

        .question-title {{
            font-family: 'Poppins', sans-serif;
            font-size: 16px;
            font-weight: 500;
            margin-bottom: 4px;
            color: var(--text-dark);
        }}

        .response-count {{
            font-size: 12px;
            color: var(--text-gray);
            margin-bottom: 16px;
        }}

        /* Text Responses List */
        .response-list {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            max-height: 400px;
            overflow-y: auto;
            padding-right: 8px;
        }}

        /* Scrollbar for response list */
        .response-list::-webkit-scrollbar {{
            width: 8px;
        }}
        .response-list::-webkit-scrollbar-track {{
            background: #f1f1f1; 
            border-radius: 4px;
        }}
        .response-list::-webkit-scrollbar-thumb {{
            background: #c1c1c1; 
            border-radius: 4px;
        }}
        .response-list::-webkit-scrollbar-thumb:hover {{
            background: #a8a8a8; 
        }}

        .response-item {{
            background: var(--response-bg);
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 14px;
            color: var(--text-dark);
            border: 1px solid transparent;
        }}

        .response-item:hover {{
            background: #f1f3f4;
        }}

        .chart-container {{
            width: 100%;
            max-width: 500px;
            margin: 0 auto;
            position: relative;
        }}

        @media (max-width: 600px) {{
            .header-card, .question-card {{
                padding: 16px;
            }}
            .header-title {{
                font-size: 24px;
            }}
            .header-total {{
                font-size: 20px;
            }}
        }}
    </style>
</head>
<body>

    <div class="container">
        <!-- Header Section -->
        <div class="header-card">
            <img src="assets/logo.png" alt="Logo PSB" class="logo" onerror="this.style.display='none'">
            <h1 class="header-title">Laporan Rangkuman PSB 2026</h1>
            <p class="header-desc">Dokumentasi data pendaftar Pusat Pendidikan Tahfidzul Qur'an Jamal Yusuf Al Haddad. Laporan ini menyerupai format rangkuman profesional layaknya Google Forms.</p>
            <div class="header-total">{total_responses} tanggapan</div>
        </div>

        <!-- Nama Lengkap Card -->
        <div class="question-card">
            <div class="question-title">Nama Lengkap</div>
            <div class="response-count">{total_responses} tanggapan</div>
            <div class="response-list">
"""

for nama in nama_list:
    if nama.strip():
        html_content += f'                <div class="response-item">{nama}</div>\n'

html_content += f"""            </div>
        </div>

        <!-- Tempat Lahir Card -->
        <div class="question-card">
            <div class="question-title">Tempat Lahir</div>
            <div class="response-count">{total_responses} tanggapan</div>
            <div class="response-list">
"""

for tempat in tempat_lahir_list:
    if tempat.strip():
        html_content += f'                <div class="response-item">{tempat}</div>\n'

html_content += f"""            </div>
        </div>

        <!-- Alamat Lengkap Card -->
        <div class="question-card">
            <div class="question-title">Alamat Lengkap (Desa/Kec/Kab/Prov)</div>
            <div class="response-count">{total_responses} tanggapan</div>
            <div class="response-list">
"""

for alamat in alamat_list:
    if alamat.strip():
        html_content += f'                <div class="response-item">{alamat}</div>\n'

html_content += f"""            </div>
        </div>

        <!-- Jenjang Pendidikan Card (Chart) -->
        <div class="question-card">
            <div class="question-title">Jenjang Pendidikan</div>
            <div class="response-count">{total_responses} tanggapan</div>
            <div class="chart-container">
                <canvas id="jenjangChart"></canvas>
            </div>
        </div>
        
    </div>

    <script>
        // Data for Jenjang Pendidikan Chart
        const jenjangLabels = {json.dumps(jenjang_labels)};
        const jenjangData = {json.dumps(jenjang_data)};
        
        const ctx = document.getElementById('jenjangChart').getContext('2d');
        new Chart(ctx, {{
            type: 'pie',
            data: {{
                labels: jenjangLabels,
                datasets: [{{
                    data: jenjangData,
                    backgroundColor: [
                        '#4285F4', // Google Blue
                        '#EA4335', // Google Red
                        '#FBBC05', // Google Yellow
                        '#34A853'  // Google Green
                    ],
                    borderWidth: 1,
                    borderColor: '#ffffff'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        position: 'right',
                        labels: {{
                            font: {{
                                family: "'Poppins', sans-serif",
                                size: 14
                            }},
                            color: '#202124'
                        }}
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                let label = context.label || '';
                                if (label) {{
                                    label += ': ';
                                }}
                                const value = context.raw;
                                const total = context.chart._metasets[context.datasetIndex].total;
                                const percentage = Math.round((value / total) * 100) + '%';
                                label += value + ' (' + percentage + ')';
                                return label;
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

output_path = os.path.join(base_dir, "dokumentasi.html")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Laporan Dokumentasi (GForm style) berhasil dibuat di {output_path}")
