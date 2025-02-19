# src/ui/map_panel.py
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
import logging
import os

class MapWebPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line, source):
        logging.debug(f"JS Console [{level}] Line {line}: {message}")
        
    def certificateError(self, error):
        # Allow all certificates to avoid possible SSL issues
        return True

class MapPanel(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # Using a custom WebPage
        self.setPage(MapWebPage(self))
        
        # Correctly accessing WebAttribute
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        
        # Set the initial page
        self.setHtml("""
        <html>
            <head>
                <style>
                    body, html {
                        margin: 0;
                        padding: 0;
                        width: 100%;
                        height: 100%;
                    }
                </style>
            </head>
            <body>
                <h2 style='text-align:center;margin-top:40%;color:#666;font-family:sans-serif'>
                    Map visualization will appear here
                </h2>
            </body>
        </html>
        """)
        
        self.loadFinished.connect(self._on_load_finished)
    
    def update_map(self, html_path: str):
        """Load a map from a file"""
        if not html_path or not os.path.exists(html_path):
            self.logger.warning(f"Invalid map file path: {html_path}")
            return
            
        try:
            self.logger.debug(f"Loading map file: {html_path}")
            file_url = QUrl.fromLocalFile(os.path.abspath(html_path))
            self.logger.debug(f"File URL: {file_url.toString()}")
            
            # Load file URL directly
            self.load(file_url)
            
        except Exception as e:
            self.logger.error(f"Error loading map: {str(e)}", exc_info=True)
    
    def _on_load_finished(self, success: bool):
        self.logger.debug(f"Page load finished: {success}")
        if success:
            # Add CSS to ensure the legend is displayed on top
            self.page().runJavaScript("""
                (function() {
                    // Add CSS styles
                    var style = document.createElement('style');
                    style.textContent = `
                        .legend {
                            background-color: white;
                            padding: 10px;
                            border-radius: 5px;
                            box-shadow: 0 0 10px rgba(0,0,0,0.2);
                            position: absolute !important;
                            z-index: 1000 !important;
                            bottom: 30px;
                            right: 10px;
                        }
                        .folium-map {
                            z-index: 1;
                        }
                        .leaflet-control-container {
                            z-index: 999;
                        }
                    `;
                    document.head.appendChild(style);
                    
                    // Make sure all legend elements have the correct z-index
                    document.querySelectorAll('.legend').forEach(function(legend) {
                        legend.style.zIndex = '1000';
                        // Output the current style of the legend for debugging purposes
                        console.log('Legend style:', 
                            'z-index:', window.getComputedStyle(legend).zIndex,
                            'position:', window.getComputedStyle(legend).position
                        );
                    });
                    
                    // Check if the legend exists and is visible
                    var legendElements = document.querySelectorAll('.legend');
                    console.log('Found legend elements:', legendElements.length);
                    
                    return {
                        legendCount: legendElements.length,
                        legendVisible: Array.from(legendElements).map(el => 
                            window.getComputedStyle(el).display !== 'none'
                        )
                    };
                })();
            """, self._handle_legend_check)
            
            self.page().runJavaScript("""
                (function() {
                    try {
                        console.log('Checking map elements...');
                        return {
                            hasLeaflet: typeof L !== 'undefined',
                            mapElements: document.querySelectorAll('.folium-map').length,
                            bodyContent: document.body.innerHTML.length
                        };
                    } catch (e) {
                        console.error('Error in debug check:', e);
                        return {error: e.toString()};
                    }
                })();
            """, self._handle_debug_info)
            
            # Map refresh
            self.page().runJavaScript("""
                (function() {
                    try {
                        if (typeof L !== 'undefined') {
                            console.log('Leaflet found, refreshing maps...');
                            window.dispatchEvent(new Event('resize'));
                            document.querySelectorAll('.folium-map').forEach(function(map) {
                                if (map._leaflet_map) {
                                    map._leaflet_map.invalidateSize(true);
                                }
                            });
                        }
                    } catch (e) {
                        console.error('Error in map refresh:', e);
                    }
                })();
            """)
    
    def _handle_legend_check(self, info):
        """Process legend check results"""
        if info:
            self.logger.debug(f"Legend check results: {info}")
            if info.get('legendCount', 0) > 0:
                self.logger.debug("Legend elements found and styled")
            else:
                self.logger.debug("No legend elements found")
                
    def _handle_debug_info(self, debug_info):
        """Handle debug information callback"""
        if debug_info:
            self.logger.debug(f"Map debug info: {debug_info}")
            if debug_info.get('hasLeaflet'):
                self.logger.debug("Leaflet library loaded successfully")
            if debug_info.get('mapElements'):
                self.logger.debug(f"Found {debug_info['mapElements']} map elements")
            if debug_info.get('error'):
                self.logger.error(f"Debug error: {debug_info['error']}")