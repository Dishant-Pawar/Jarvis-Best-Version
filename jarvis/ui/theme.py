# JARVIS UI Styling Specifications

DARK_THEME_STYLE = """
    #MainFrame {
        background-color: rgba(15, 15, 25, 215);
        border: 1.5px solid rgba(0, 240, 255, 100);
        border-radius: 16px;
    }
    
    QLabel {
        color: #e2e8f0;
        font-family: 'Segoe UI', 'Outfit', 'Inter', sans-serif;
    }
    
    #TitleLabel {
        font-size: 13px;
        font-weight: 700;
        color: #00f0ff;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    #StatusLabel {
        font-size: 11px;
        font-weight: 500;
        color: #94a3b8;
    }
    
    #ResponseLabel {
        font-size: 11px;
        color: #cbd5e1;
        font-style: italic;
    }
    
    #ControlBtn {
        background-color: transparent;
        color: #64748b;
        font-weight: bold;
        font-size: 12px;
        border: none;
        border-radius: 6px;
        min-width: 24px;
        min-height: 24px;
        max-width: 24px;
        max-height: 24px;
    }
    
    #ControlBtn:hover {
        background-color: rgba(255, 255, 255, 20);
        color: #00f0ff;
    }
    
    #ControlBtnClose:hover {
        background-color: rgba(239, 68, 68, 200);
        color: #ffffff;
    }

    #MicButton {
        background-color: rgba(0, 240, 255, 15);
        border: 1.5px solid rgba(0, 240, 255, 70);
        border-radius: 22px;
        min-width: 44px;
        min-height: 44px;
        max-width: 44px;
        max-height: 44px;
    }
    
    #MicButton:hover {
        background-color: rgba(0, 240, 255, 30);
        border: 2px solid rgba(0, 240, 255, 150);
    }
    
    #MicButton:pressed {
        background-color: rgba(0, 240, 255, 60);
        border: 2px solid #00f0ff;
    }

    /* Listening state mic button color */
    #MicButton[listening="true"] {
        background-color: rgba(239, 68, 68, 25);
        border: 1.5px solid rgba(239, 68, 68, 120);
    }
    
    #MicButton[listening="true"]:hover {
        background-color: rgba(239, 68, 68, 40);
        border: 2px solid rgba(239, 68, 68, 200);
    }

    #ActionButton {
        background-color: rgba(255, 255, 255, 10);
        border: 1px solid rgba(255, 255, 255, 20);
        border-radius: 6px;
        color: #cbd5e1;
        font-family: 'Segoe UI', sans-serif;
        font-size: 11px;
        padding: 4px 10px;
    }
    
    #ActionButton:hover {
        background-color: rgba(0, 240, 255, 20);
        border: 1px solid rgba(0, 240, 255, 80);
        color: #ffffff;
    }
    
    #ActionButton:pressed {
        background-color: rgba(0, 240, 255, 40);
    }
"""
