import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import json
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="NOC Meru Networks - Analizador",
    page_icon="📡",
    layout="wide"
)

# Estilos CSS personalizados para la identidad visual de Meru
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 15px 25px;
        border-bottom: 3px solid #00adef;
        background-color: white;
        margin-bottom: 25px;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stExpander {
        border: none !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        background: white;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

def render_summary_cards(summary_data):
    """
    Renderiza tarjetas de resumen usando React/Tailwind para un look profesional.
    """
    json_data = json.dumps(summary_data)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-transparent">
        <div id="root"></div>
        <script type="text/babel">
            const App = () => {{
                const items = {json_data};
                return (
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-1">
                        {{items.map((item, i) => (
                            <div key={{i}} class="bg-white p-4 rounded-xl shadow-sm border-l-4 border-blue-600 flex flex-col justify-center">
                                <span class="text-gray-400 text-xs font-bold uppercase tracking-wider">{{item.label}}</span>
                                <span class="text-xl font-extrabold text-slate-800 mt-1">{{item.value}}</span>
                            </div>
                        ))}}
                    </div>
                );
            }};
            const root = ReactDOM.createRoot(document.getElementById('root'));
            root.render(<App />);
        </script>
    </body>
    </html>
    """
    components.html(html_content, height=110)

def get_clean_df(file):
    """Limpia el CSV saltando metadatos de iDirect hasta encontrar la cabecera"""
    content = file.getvalue().decode('utf-8', errors='ignore').splitlines()
    skip_rows = 0
    for i, line in enumerate(content):
        if any(key in line for key in ["Date", "Time", "Octets", "Bit Rate", "Eb/No"]):
            skip_rows = i
            break
    file.seek(0)
    try:
        df = pd.read_csv(file, skiprows=skip_rows)
        df.columns = [str(c).strip().replace('"', '') for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return pd.DataFrame()

def analyze_usage(df):
    """Procesamiento de Consumo de Datos (In/Out) con diseño de Dashboard"""
    all_cols = df.columns.tolist()
    sites = sorted(list(set([c.split('/')[0] for c in all_cols if '/' in c])))
    
    if not sites:
        st.warning("Formato no reconocido para análisis de estaciones.")
        return

    report = []
    for s in sites:
        in_c = next((c for c in all_cols if c.startswith(s + "/") and any(k in c for k in ["In", "FL"])), None)
        out_c = next((c for c in all_cols if c.startswith(s + "/") and any(k in c for k in ["Out", "RL"])), None)
        
        if in_c or out_c:
            val_in = pd.to_numeric(df[in_c], errors='coerce').sum() if in_c else 0
            val_out = pd.to_numeric(df[out_c], errors='coerce').sum() if out_c else 0
            
            is_bytes = "Octets" in str(in_c or out_c)
            factor = (1024 * 1024) if is_bytes else 1
            unit = "MB" if is_bytes else "Units"

            if (val_in + val_out) > 0:
                report.append({
                    "Estación": s,
                    f"In ({unit})": round(val_in / factor, 2),
                    f"Out ({unit})": round(val_out / factor, 2),
                    f"Total ({unit})": round((val_in + val_out) / factor, 2)
                })

    if report:
        res_df = pd.DataFrame(report).sort_values(by=f"Total ({unit})", ascending=False)
        
        # Resumen superior
        summary_data = [
            {"label": "Tráfico Total", "value": f"{res_df[f'Total ({unit})'].sum():,.2f} {unit}"},
            {"label": "Estaciones Activas", "value": str(len(res_df))},
            {"label": "Máximo Consumo", "value": res_df.iloc[0]['Estación']},
            {"label": "Promedio", "value": f"{res_df[f'Total ({unit})'].mean():,.2f} {unit}"}
        ]
        render_summary_cards(summary_data)

        # Gráfica y Tabla
        c1, c2 = st.columns([1.5, 1])
        with c1:
            fig = px.bar(res_df.head(15), x=f"Total ({unit})", y="Estación", orientation='h',
                         title="Ranking de Consumo (Top 15)", 
                         color=f"Total ({unit})", color_continuous_scale="Blues")
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.markdown("#### Detalle por Estación")
            st.dataframe(res_df, use_container_width=True, hide_index=True)

def analyze_signal(df):
    """Procesamiento de Niveles de Señal y Eb/No con enfoque histórico"""
    st.markdown("### 📶 Monitoreo de Señal")
    all_cols = df.columns.tolist()
    time_col = next((c for c in all_cols if "Date" in c or "Time" in c), None)
    stations = sorted(list(set([c.split('/')[0] for c in all_cols if '/' in c])))
    
    if not stations:
        st.error("No se encontraron series de datos de señal.")
        return

    selected = st.selectbox("Seleccione Estación para inspección:", stations)
    
    if selected:
        plot_cols = [c for c in all_cols if c.startswith(selected + "/")]
        fig = go.Figure()
        x_axis = df[time_col] if time_col else df.index
        
        for c in plot_cols:
            fig.add_trace(go.Scatter(x=x_axis, y=df[c], name=c.split('/')[-1], mode='lines'))
            
        fig.update_layout(
            title=f"Historial de Señal: {selected}", 
            template="plotly_white", 
            hovermode="x unified",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

def main():
    # Encabezado corporativo
    st.markdown(f"""
        <div class="header-container">
            <div style="display: flex; flex-direction: column;">
                <h1 style="color: #1e3a8a; margin: 0; font-size: 24px;">MERU NETWORKS NOC</h1>
                <span style="color: #00adef; font-weight: 500; font-size: 14px;">PLATAFORMA DE ANÁLISIS DE RED</span>
            </div>
            <img src="https://merunetworks.com.ve/wp-content/uploads/2021/04/Logo-Meru-Networks-01.png" width="160">
        </div>
    """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.markdown("### Centro de Carga 📂")
    files = st.sidebar.file_uploader("Subir reportes CSV", type="csv", accept_multiple_files=True)
    
    st.sidebar.markdown("---")
    st.sidebar.info("Herramienta diseñada para el procesamiento de archivos iDirect NMS.")

    if not files:
        st.markdown("""
            <div style="text-align: center; padding: 50px; color: #64748b;">
                <h2>Listo para procesar datos</h2>
                <p>Por favor, cargue los archivos CSV en el panel lateral para generar el reporte visual.</p>
            </div>
        """, unsafe_allow_html=True)
        return

    # Procesamiento de archivos
    for f in files:
        with st.expander(f"📦 Reporte: {f.name}", expanded=True):
            df = get_clean_df(f)
            if df.empty:
                continue
                
            cols_text = " ".join(df.columns).lower()
            if any(k in cols_text for k in ["octets", "bit rate", "fl bit", "rl bit"]):
                analyze_usage(df)
            else:
                analyze_signal(df)

if __name__ == "__main__":
    main()
