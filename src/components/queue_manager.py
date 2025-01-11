import streamlit as st
import time
import random
from ..config.constants import RESOLUTIONS
from ..utils.validation import validate_resolution
from ..utils.screenshot import setup_webdriver, capture_screenshot

# Mensajes divertidos para el proceso de captura
LOADING_MESSAGES = [
    "🤖 Preparando los robots capturadores...",
    "📸 Ajustando el lente virtual...",
    "🎨 Mezclando los píxeles perfectos...",
    "🚀 Iniciando los motores de captura...",
    "🎯 Apuntando al objetivo...",
    "🌈 Calibrando los colores...",
    "🔍 Enfocando la página...",
    "⚡ Cargando los súper poderes...",
    "🎪 Preparando el espectáculo...",
    "🎭 Poniéndonos la máscara de captura...",
]

def process_screenshots(selected_resolutions):
    """Process screenshots for all URLs in queue"""
    st.session_state.screenshots_data = {}
    
    # Crear contenedor para la barra de progreso
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    message_placeholder = st.empty()
    
    driver = setup_webdriver()
    if driver is None:
        st.error("No se pudo inicializar el navegador. Por favor, verifica la instalación de Chrome y ChromeDriver en el servidor.")
        return
        
    total_tasks = len(st.session_state.urls_queue) * len(selected_resolutions)
    completed_tasks = 0
    
    try:
        with st.spinner('Iniciando el proceso de captura...'):
            for url_idx, url in enumerate(st.session_state.urls_queue):
                st.session_state.screenshots_data[url] = {}
                
                for res_idx, resolution_name in enumerate(selected_resolutions):
                    # Actualizar mensajes y progreso
                    progress = completed_tasks / total_tasks
                    progress_placeholder.progress(progress)
                    
                    message = random.choice(LOADING_MESSAGES)
                    status_placeholder.markdown(f"<h3 style='text-align: center'>🎯 Procesando URL {url_idx + 1} de {len(st.session_state.urls_queue)}</h3>", unsafe_allow_html=True)
                    message_placeholder.markdown(f"<p style='text-align: center'>{message}</p>", unsafe_allow_html=True)
                    
                    # Capturar screenshot
                    width, height = RESOLUTIONS[resolution_name]
                    status = st.status(f"📸 {url} - {resolution_name}", expanded=False)
                    status.update(label=f"⏳ Capturando {resolution_name}...", state="running")
                    
                    screenshot = capture_screenshot(driver, url, width, height)
                    if screenshot:
                        st.session_state.screenshots_data[url][resolution_name] = screenshot
                        status.update(label=f"✨ {resolution_name} capturada exitosamente", state="complete")
                    else:
                        status.update(label=f"❌ Error al capturar {resolution_name}", state="error")
                    
                    completed_tasks += 1
                    time.sleep(0.1)  # Pequeña pausa para ver la animación
            
            if completed_tasks > 0:
                # Mostrar progreso final
                progress_placeholder.progress(1.0)
                status_placeholder.markdown("<h3 style='text-align: center'>✨ ¡Proceso completado!</h3>", unsafe_allow_html=True)
                message_placeholder.markdown("<p style='text-align: center'>Todas las capturas han sido procesadas exitosamente</p>", unsafe_allow_html=True)
                
                # Efectos de celebración
                st.balloons()
                st.success("¡Todas las capturas han sido completadas con éxito! 🎉")
                
                st.session_state.show_results = True
                time.sleep(1)
                st.rerun()
    
    finally:
        if driver:
            driver.quit()

def queue_manager_section():
    """Component for managing URL queue and screenshot settings"""
    if not st.session_state.urls_queue:
        return

    with st.container():
        st.markdown("<div class='section-container'>", unsafe_allow_html=True)
        st.subheader("URL Queue")
        
        with st.expander("View Queue", expanded=True):
            for idx, url in enumerate(st.session_state.urls_queue):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(f"{idx + 1}. {url}")
                with col2:
                    if st.button("🗑️", key=f"remove_{idx}", type="secondary", help="Remove URL"):
                        st.session_state.urls_queue.pop(idx)
                        st.rerun()
            
            if st.button("Clear Queue", type="secondary", key="clear_queue", help="Remove all URLs", use_container_width=True):
                st.session_state.urls_queue = []
                st.rerun()
        
        # Resolution Selection
        st.subheader("Screenshot Settings")
        selected_resolutions = st.multiselect(
            "Select Resolutions",
            options=list(RESOLUTIONS.keys()),
            default=["Desktop (1920x1080)"],
            help="Choose one or more resolutions for your screenshots"
        )
        
        # Custom Resolution
        custom_resolution = st.text_input(
            "Custom Resolution (optional)",
            placeholder="e.g., 1200x800",
            help="Enter a custom resolution in WIDTHxHEIGHT format"
        )
        
        if custom_resolution and validate_resolution(custom_resolution):
            width, height = map(int, custom_resolution.split('x'))
            resolution_name = f"Custom ({width}x{height})"
            RESOLUTIONS[resolution_name] = (width, height)
            if resolution_name not in selected_resolutions:
                selected_resolutions.append(resolution_name)
        elif custom_resolution:
            st.error("Invalid resolution format. Use WIDTHxHEIGHT (e.g., 1200x800)")
        
        if st.button("🚀 Generate Screenshots", type="primary", disabled=not selected_resolutions, use_container_width=True):
            process_screenshots(selected_resolutions)
        
        st.markdown("</div>", unsafe_allow_html=True) 