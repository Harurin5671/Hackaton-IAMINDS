def get_ethics_disclaimer():
    """
    Returns the ethics disclaimer text.
    """
    return """
    ### 🛡️ Declaración de Ética y Transparencia (GhostEnergy AI)
    
    **1. Propósito del Sistema:**
    Este sistema utiliza Inteligencia Artificial para optimizar el consumo energético en sedes de la UPTC. Su objetivo es reducir la huella de carbono y los costos operativos sin comprometer el bienestar de la comunidad universitaria.
    
    **2. Origen de los Datos:**
    Los datos históricos son generados sintéticamente basados en patrones teóricos de consumo y ocupación. No se utilizan datos personales reales para este prototipo.
    
    **3. Limitaciones del Modelo:**
    - Los modelos predictivos (XGBoost) y de detección de anomalías (Isolation Forest) tienen un margen de error.
    - Las recomendaciones deben ser validadas por personal técnico antes de su implementación.
    - El asistente de IA puede alucinar información; verifique siempre los datos crudos en el dashboard.
    
    **4. Privacidad:**
    No se recolectan datos biométricos ni de identificación personal. El monitoreo de ocupación es anónimo y agregado.
    
    **5. Impacto Ambiental:**
    El sistema estima la reducción de CO2 basada en factores de emisión promedio de la red eléctrica colombiana (aprox. 164g CO2/kWh).
    """
