import streamlit as st
import pandas as pd
import random
import os
import time
import base64
import json
import pycountry
import plotly.express as px
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Horse Racing Racetrack Randomizer", layout="wide", initial_sidebar_state="expanded")

# --- UI Alignment CSS ---
st.markdown("""
<style>
/* Reset global padding to allow containers to touch the top header */
[data-testid="stMainBlockContainer"] {
    padding-top: 1rem !important;
}

/* Ensure columns always start from the absolute top */
[data-testid="stHorizontalBlock"] {
    align-items: flex-start !important;
}

/* Strip inner widget margins that cause micro-misalignments */
[data-testid="column"] [data-testid="stVerticalBlock"] {
    padding-top: 0rem !important;
}
</style>
""", unsafe_allow_html=True)

# --- CSS Injection ---
# Esports theme: Dark backgrounds, neon accents, distinct badges.
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return ""

def inject_css():
    bg_base64 = get_base64_of_bin_file('racetrack_bg.png')
    if bg_base64:
        st.markdown(f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(10, 10, 10, 0.85), rgba(10, 10, 10, 0.85)), url("data:image/png;base64,{bg_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """, unsafe_allow_html=True)
        
    st.markdown("""
    <style>
    /* Global styles */
    .stApp {
        background-color: #0A0A0A;
        color: #efeff1;
        font-family: 'Inter', sans-serif;
    }
    
    /* Maximize Viewport: Ghost Header */
    [data-testid="stHeader"] {
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }
    
    /* Hide specific Streamlit clutter specifically */
    button[aria-label="Deploy"], 
    button[aria-label="View menu"] {
        display: none !important;
    }
    
    /* MINIMAL WHITE TAB: Sidebar Toggle Design */
    /* Target Open and Closed states with fixed positioning */
    [data-testid="stSidebarCollapsedControl"],
    button[aria-label="Collapse sidebar"] {
        display: flex !important;
        visibility: visible !important;
        position: fixed !important;
        top: 100px !important; 
        width: 32px !important;
        height: 60px !important;
        background: #ffffff !important; 
        border: 1px solid #cccccc !important;
        z-index: 10000001 !important;
        cursor: pointer !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 2px 0 8px rgba(0,0,0,0.1) !important;
        transition: all 0.2s ease !important;
    }

    /* State 1: Sidebar is COLLAPSED (Expand button) */
    [data-testid="stSidebarCollapsedControl"] {
        left: 0 !important;
        border-left: none !important;
        border-radius: 0 4px 4px 0 !important;
    }

    /* State 2: Sidebar is OPEN (Collapse button) */
    button[aria-label="Collapse sidebar"] {
        left: 336px !important; /* Fixed to the standard sidebar width edge */
        border-radius: 0 4px 4px 0 !important;
        border-left: none !important;
    }
    
    /* Hide specific Streamlit clutter */
    [data-testid="stHeader"] button[aria-label="Deploy"], 
    [data-testid="stHeader"] button[aria-label="View menu"],
    button[kind="header"]:has(span:contains("Deploy")) {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Inject Arrows */
    /* Target the Expand button (left side) specifically */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    .st-emotion-cache-6qob1r {
        background-color: rgba(0,0,0,0.6) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }

    [data-testid="collapsedControl"]::after,
    [data-testid="stSidebarCollapsedControl"]::after,
    .st-emotion-cache-6qob1r::after {
        content: "»" !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        height: 100% !important;
        line-height: 1 !important;
    }

    button[aria-label="Collapse sidebar"]::after {
        content: "◀" !important;
        color: #666666 !important;
        -webkit-text-fill-color: #666666 !important;
        font-size: 14px !important;
        margin-right: 2px;
    }
    
    /* Hide ALL native icons in header and sidebar toggles */
    [data-testid="stHeader"] svg,
    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] svg,
    button[aria-label="Collapse sidebar"] svg {
        display: none !important;
        visibility: hidden !important;
    }

    /* Force the expand button background to be dark/transparent to show white icon */
    [data-testid="stSidebarCollapsedControl"], 
    button[kind="header"] {
        background-color: rgba(0,0,0,0.4) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #ffffff !important;
    }

    [data-testid="stSidebarCollapsedControl"]:hover,
    button[aria-label="Collapse sidebar"]:hover {
        background: #f8f9fa !important;
        width: 36px !important;
    }

    [data-testid="stSidebarCollapsedControl"]:hover,
    button[aria-label="Collapse sidebar"]:hover {
        background: #f0f0f0 !important;
    }

    /* Satellite HUD Map Styling */
    [data-testid="stPlotlyChart"] {
        border: 1px solid rgba(0, 242, 255, 0.2) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.1) !important;
    }
    .modebar { display: none !important; }
    
    .hud-label {
        font-family: 'Courier New', Courier, monospace !important;
        color: #FFFF00 !important;
        text-shadow: 0 0 8px rgba(255, 255, 0, 0.6) !important;
        font-weight: bold !important;
        font-size: 0.85em !important;
        letter-spacing: 1px !important;
    }
    
    .race-card {
        border-radius: 12px 12px 0 0;
        padding: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.4);
        display: flex;
        flex-direction: column;
        color: #ffffff;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .race-card-selected {
        border: 2px solid #bf94ff !important;
        border-bottom: none !important;
        box-shadow: 0 0 15px rgba(191, 148, 255, 0.3);
        background: rgba(191, 148, 255, 0.05) !important;
    }
    
    .stButton > button {
        border-radius: 0 0 12px 12px !important;
        border-top: none !important;
        font-size: 0.8em !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        background: rgba(255,255,255,0.05) !important;
        height: 32px !important;
    }
    
    .stButton > button:hover {
        background: rgba(191, 148, 255, 0.2) !important;
        color: #bf94ff !important;
        border-color: #bf94ff !important;
    }
    
    /* Rank Gradients */
    .bg-1 { background: linear-gradient(135deg, #443c11 0%, #1a180b 100%); border-left: 5px solid #FFD700 !important; }
    .bg-2 { background: linear-gradient(135deg, #2e2e2e 0%, #121212 100%); border-left: 5px solid #C0C0C0 !important; }
    .bg-3 { background: linear-gradient(135deg, #422811 0%, #170d05 100%); border-left: 5px solid #CD7F32 !important; }
    .bg-4 { background: linear-gradient(135deg, #0b2f4f 0%, #03101c 100%); border-left: 5px solid #0078D7 !important; }
    .bg-0 { background: linear-gradient(135deg, #262626 0%, #121212 100%); border-left: 5px solid #777777 !important; }
    
    .race-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 10px;
        margin-bottom: 10px;
    }
    
    /* Badges */
    .badge {
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        font-weight: bold;
        text-transform: uppercase;
        color: #fff;
    }
    .badge-g1 { background-color: #FFD700; color: #000; } /* Gold */
    .badge-g2 { background-color: #C0C0C0; color: #000; } /* Silver */
    .badge-g3 { background-color: #CD7F32; } /* Bronze */
    .badge-local { background-color: #0078D7; } /* Blue */
    .badge-none { background-color: #555555; } /* Grey */
    
    .badge-turf { background-color: #2e8b57; }
    .badge-dirt { background-color: #8b4513; }
    .badge-synthetic { background-color: #696969; }

    /* Race Name Typography */
    .race-name-official {
        font-size: 1.2em;
        font-weight: 800;
        color: #ffffff;
    }
    /* Sidebar card optimization */
    [data-testid="stSidebar"] .race-card {
        padding: 6px !important;
    }
    [data-testid="stSidebar"] .race-card div {
        font-size: 0.85em !important;
    }
    [data-testid="stSidebar"] .race-card .badge {
        font-size: 0.7em !important;
        padding: 1px 4px !important;
    }

    .race-name-generic {
        font-size: 1.1em;
        font-weight: 500;
        color: #e0e0e0;
    }

    /* Streamlit Expander & Form Contrast Fixes */
    .stExpander div[data-testid="stExpanderDetails"] label p {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.95em !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    }
    
    .stExpander div[data-testid="stExpanderDetails"] {
        background-color: rgba(0,0,0,0.4) !important;
        border-radius: 0 0 8px 8px;
    }

    .stExpander summary {
        font-weight: 700 !important;
        color: #bf94ff !important;
    }

    /* Clear Slot Button styling */
    div.stButton > button:contains("CLEAR SLOT") {
        border: 1px solid rgba(255, 75, 75, 0.3) !important;
        background-color: rgba(255, 75, 75, 0.05) !important;
        color: #ff4b4b !important;
        font-weight: 700 !important;
    }
    div.stButton > button:contains("CLEAR SLOT"):hover {
        background-color: rgba(255, 75, 75, 0.2) !important;
        border-color: #ff4b4b !important;
    }

    /* === REFINED SIDEBAR STYLING === */
    /* Target only the main containers for background, not every div */
    [data-testid="stSidebar"] .stExpander,
    [data-testid="stSidebar"] [data-testid="stExpanderDetails"],
    [data-testid="stSidebar"] [data-testid="stExpanderDetails"] [data-testid="stVerticalBlock"] {
        background-color: #ffffff !important;
        border-color: #e0e0e0 !important;
    }

    /* Remove the 'embossed' or blurry look from sidebar text */
    [data-testid="stSidebar"] .stExpander * {
        text-shadow: none !important;
        filter: none !important;
    }

    /* Remove the padding that causes the 'grey frame' look */
    [data-testid="stSidebar"] [data-testid="stExpanderDetails"] {
        padding: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpanderDetails"] > div {
        padding: 10px !important;
    }

    /* Force all widget text in sidebar expanders to be solid black */
    [data-testid="stSidebar"] .stExpander [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] .stExpander .stMarkdown p,
    [data-testid="stSidebar"] .stExpander .stCaption,
    [data-testid="stSidebar"] .stExpander span:not(.badge):not(.race-card-text) {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        text-shadow: none !important;
    }

    /* RESTORE RACE CARD TEXT (Stable Cards) - Excluding Badges */
    .race-card, .race-card div, .race-card p {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }
    .race-card span:not(.badge) {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }

    /* Improved Input/Button Contrast in Sidebar */
    [data-testid="stSidebar"] .stExpander input,
    [data-testid="stSidebar"] .stExpander .stSelectbox [data-testid="stWidgetLabel"] + div {
        border: 1px solid #cccccc !important;
        background-color: #fcfcfc !important;
        color: #000000 !important;
        box-shadow: none !important;
    }
    /* Make the red focus "thing" invisible */
    [data-testid="stSidebar"] .stExpander input:focus,
    [data-testid="stSidebar"] .stExpander .stSelectbox [data-testid="stWidgetLabel"] + div:focus-within {
        border-color: #aaaaaa !important;
        box-shadow: none !important;
        outline: none !important;
    }

    [data-testid="stSidebar"] .stExpander button {
        border: 1px solid #dddddd !important;
        background-color: #ffffff !important;
        transition: all 0.2s ease;
        font-weight: 700 !important;
    }

    /* Library Action Buttons (Below Cards) - Borderless & Standout */
    [data-testid="stSidebar"] .stExpander button[key^="sel_lib_"],
    [data-testid="stSidebar"] .stExpander button[key^="up_"],
    [data-testid="stSidebar"] .stExpander button[key^="down_"],
    [data-testid="stSidebar"] .stExpander button[key^="del_stable_"] {
        border: none !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
    }

    /* Pickup Button */
    [data-testid="stSidebar"] button[key^="sel_lib_"] {
        background-color: #e3f2fd !important;
        color: #1976d2 !important;
    }
    /* Move Buttons */
    [data-testid="stSidebar"] button[key^="up_"], [data-testid="stSidebar"] button[key^="down_"] {
        background-color: #eeeeee !important;
        color: #444444 !important;
    }
    /* Stable Item Delete */
    [data-testid="stSidebar"] button[key^="del_stable_"] {
        background-color: #ffebee !important;
        color: #c62828 !important;
    }

    /* Metallic Badge Effects - Forced High Priority */

    [data-testid="stSidebar"] .stExpander summary {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: 800 !important;
        padding: 12px !important;
        border-bottom: 1px solid #eeeeee !important;
    }

    /* Prevent the black override from breaking the toggle switch color itself */
    [data-testid="stSidebar"] .stExpander [data-testid="stWidgetLabel"] div {
        color: inherit !important;
    }
    
    [data-testid="stSidebar"] .stExpander .stCaption {
        color: #333333 !important;
        font-weight: 500 !important;
    }

    /* Global Metallic Badge Design System (Works in all Card types) */
    .metallic-badge, .badge-g2-metallic, .badge-g3-metallic {
        font-weight: 800 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
        padding: 2px 8px !important;
        border-radius: 4px !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    
    .metallic-badge {
        background: linear-gradient(135deg, #ffd700 0%, #fff8a0 50%, #d4af37 100%) !important;
    }
    .badge-g2-metallic {
        background: linear-gradient(135deg, #c0c0c0 0%, #f0f0f0 50%, #808080 100%) !important;
    }
    .badge-g3-metallic {
        background: linear-gradient(135deg, #cd7f32 0%, #ffc080 50%, #8b4513 100%) !important;
    }

    /* Glassmorphism 2.0 */
    .race-card {
        border-radius: 12px 12px 0 0;
        padding: 10px;
        background: rgba(10, 10, 10, 0.85) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: none; /* Handled by bg-X classes */
        box-shadow: 0 4px 15px rgba(0,0,0,0.6);
        display: flex;
        flex-direction: column;
        color: #ffffff;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden; /* For shimmer */
    }

    /* Tactical Feedback Animations */
    @keyframes success-pulse {
        0% { box-shadow: 0 0 5px rgba(0, 242, 255, 0.5); border-color: rgba(0, 242, 255, 0.5); }
        50% { box-shadow: 0 0 20px rgba(0, 242, 255, 1); border-color: rgba(0, 242, 255, 1); }
        100% { box-shadow: 0 0 5px rgba(0, 242, 255, 0.5); border-color: rgba(0, 242, 255, 0.5); }
    }
    .pulse-success {
        animation: success-pulse 0.5s ease-out;
    }

    @keyframes error-shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); border-color: red; }
        50% { transform: translateX(5px); border-color: red; }
        75% { transform: translateX(-5px); border-color: red; }
    }
    .shake-error {
        animation: error-shake 0.4s ease-in-out;
    }

    /* Prestige Shimmer Streak (G1, G2, G3) */
    .shimmer-streak::before {
        content: '';
        position: absolute;
        top: 0; left: -150%; width: 50%; height: 100%;
        background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0) 100%);
        transform: skewX(-25deg);
        animation: sweep 5s infinite;
        pointer-events: none;
    }
    @keyframes sweep {
        0% { left: -150%; }
        20% { left: 200%; }
        100% { left: 200%; }
    }

    /* G1 Major Event Pulse */
    @keyframes pulse-gold {
        0% { box-shadow: 0 0 10px rgba(255, 215, 0, 0.2); }
        50% { box-shadow: 0 0 25px rgba(255, 215, 0, 0.6); }
        100% { box-shadow: 0 0 10px rgba(255, 215, 0, 0.2); }
    }
    .glow-g1 {
        animation: pulse-gold 3s infinite ease-in-out;
        border: 1px solid rgba(255, 215, 0, 0.5) !important;
    }

    /* Metallic Badges Update */
    .metallic-badge {
        background: linear-gradient(135deg, #d4af37 0%, #f9f295 45%, #b8860b 70%, #f9f295 100%) !important;
        color: #000 !important;
        font-weight: 900 !important;
        text-shadow: 0 1px 1px rgba(255,255,255,0.3) !important;
        border: 1px solid rgba(0,0,0,0.2) !important;
    }
    
    /* Slot UI */
    .slot-timeline {
        display: flex;
        gap: 15px;
        margin-bottom: 25px;
        overflow-x: auto;
        padding: 10px 0;
    }
    
    .slot-box {
        min-width: 160px;
        height: 100px;
        background: rgba(255,255,255,0.05);
        border: 2px dashed rgba(255,255,255,0.2);
        border-radius: 12px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s;
        position: relative;
    }
    
    .slot-box:hover {
        background: rgba(191,148,255,0.1);
        border-color: #bf94ff;
    }
    
    .slot-filled {
        background: rgba(191,148,255,0.08);
        border: 2px solid #bf94ff;
    }
    
    .slot-manual-indicator {
        position: absolute;
        top: -8px;
        right: -8px;
        background: #bf94ff;
        color: #000;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        font-size: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
    }
    .full-detail-card {
        border-radius: 12px;
        padding: 15px 20px;
        margin-top: 5px;
        background-size: cover;
        background-position: center;
        position: relative;
        overflow: hidden;
        min-height: 140px;
        color: white;
        border: 2px solid rgba(255,255,255,0.15);
        box-shadow: 0 5px 20px rgba(0,0,0,0.5);
        transition: box-shadow 0.4s ease;
    }
    .full-detail-content {
        position: relative;
        z-index: 10;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }

    /* --- Condition Glow Borders --- */
    .glow-gold  { box-shadow: 0 0 18px 4px rgba(255,215,0,0.7), 0 0 40px 8px rgba(255,180,0,0.3) !important; border-color: #FFD700 !important; }
    .glow-night { box-shadow: 0 0 18px 4px rgba(140,80,255,0.7), 0 0 40px 8px rgba(80,0,200,0.3) !important; border-color: #8c50ff !important; }
    .glow-storm { animation: storm-pulse 1.5s ease-in-out infinite; border-color: rgba(200,220,255,0.6) !important; }
    @keyframes storm-pulse {
        0%,100% { box-shadow: 0 0 10px 2px rgba(200,220,255,0.4); }
        50%      { box-shadow: 0 0 28px 8px rgba(200,220,255,0.8); }
    }

    /* --- Particle Layers (z-index 2-5, below content at 10) --- */
    .particle-layer { position:absolute; inset:0; z-index:3; pointer-events:none; overflow:hidden; border-radius:12px; }

    /* Spring petals */
    .petal { position:absolute; width:8px; height:8px; background:rgba(255,150,180,0.7); border-radius:50% 0 50% 0; animation: fall-petal 6s linear infinite; opacity:0.6; }
    @keyframes fall-petal {
        0%   { transform: translateY(-20px) rotate(0deg) translateX(0); opacity:0.7; }
        100% { transform: translateY(180px) rotate(360deg) translateX(30px); opacity:0; }
    }
    .petal:nth-child(1){left:10%;animation-delay:0s;animation-duration:5s;}
    .petal:nth-child(2){left:30%;animation-delay:1.2s;animation-duration:6.5s;}
    .petal:nth-child(3){left:55%;animation-delay:0.5s;animation-duration:5.5s;}
    .petal:nth-child(4){left:75%;animation-delay:2s;animation-duration:7s;}
    .petal:nth-child(5){left:88%;animation-delay:1s;animation-duration:6s;}

    /* Summer bokeh / sundust */
    .bokeh-circle { position:absolute; border-radius:50%; background:rgba(255,210,80,0.15); animation: bokeh-drift 12s ease-in-out infinite; }
    @keyframes bokeh-drift {
        0%   { transform: translate(0,0) scale(1); opacity:0.12; }
        33%  { transform: translate(20px,-15px) scale(1.1); opacity:0.18; }
        66%  { transform: translate(-10px,10px) scale(0.9); opacity:0.10; }
        100% { transform: translate(0,0) scale(1); opacity:0.12; }
    }
    .bokeh-circle:nth-child(1){width:60px;height:60px;top:10%;left:15%;animation-delay:0s;animation-duration:10s;}
    .bokeh-circle:nth-child(2){width:40px;height:40px;top:40%;left:55%;animation-delay:2s;animation-duration:13s;}
    .bokeh-circle:nth-child(3){width:80px;height:80px;top:5%;left:70%;animation-delay:1s;animation-duration:11s;}
    .bokeh-circle:nth-child(4){width:30px;height:30px;top:60%;left:30%;animation-delay:3s;animation-duration:9s;}
    .bokeh-circle:nth-child(5){width:50px;height:50px;top:20%;left:85%;animation-delay:0.5s;animation-duration:14s;}
    /* Lens flare */
    .lens-flare { position:absolute; top:6px; right:10px; z-index:4; pointer-events:none; opacity:0.55; }

    /* Autumn leaves */
    .leaf { position:absolute; width:10px; height:10px; background:rgba(200,80,0,0.65); clip-path:polygon(50% 0%,100% 38%,82% 100%,18% 100%,0% 38%); animation: fall-leaf 8s linear infinite; }
    @keyframes fall-leaf {
        0%   { transform: translateY(-15px) rotate(0deg); opacity:0.8; }
        100% { transform: translateY(200px) rotate(540deg); opacity:0; }
    }
    .leaf:nth-child(1){left:8%;animation-delay:0s;animation-duration:7s;}
    .leaf:nth-child(2){left:40%;animation-delay:2s;animation-duration:9s;}
    .leaf:nth-child(3){left:68%;animation-delay:1s;animation-duration:8s;}
    .leaf:nth-child(4){left:85%;animation-delay:3s;animation-duration:10s;}

    /* Winter snow */
    .snowflake { position:absolute; width:5px; height:5px; background:rgba(220,240,255,0.8); border-radius:50%; animation: fall-snow 5s linear infinite; }
    @keyframes fall-snow {
        0%   { transform: translateY(-10px) translateX(0); opacity:1; }
        100% { transform: translateY(200px) translateX(15px); opacity:0; }
    }
    .snowflake:nth-child(1){left:15%;animation-delay:0s;}
    .snowflake:nth-child(2){left:35%;animation-delay:1s;}
    .snowflake:nth-child(3){left:60%;animation-delay:0.5s;}
    .snowflake:nth-child(4){left:80%;animation-delay:1.8s;}
    .snowflake:nth-child(5){left:92%;animation-delay:2.5s;}

    /* Rain streaks */
    .rain-streak { position:absolute; width:1px; height:18px; background:rgba(180,210,255,0.5); animation: streak 0.8s linear infinite; }
    @keyframes streak {
        0%   { transform: translateY(-20px) skewX(-15deg); opacity:0.8; }
        100% { transform: translateY(200px) skewX(-15deg); opacity:0; }
    }
    .rain-streak:nth-child(1){left:10%;animation-delay:0s;}
    .rain-streak:nth-child(2){left:25%;animation-delay:0.15s;}
    .rain-streak:nth-child(3){left:45%;animation-delay:0.3s;}
    .rain-streak:nth-child(4){left:65%;animation-delay:0.1s;}
    .rain-streak:nth-child(5){left:80%;animation-delay:0.45s;}
    .rain-streak:nth-child(6){left:92%;animation-delay:0.25s;}

    /* Ground / Wear */
    .wear-bar-track { background:rgba(255,255,255,0.2); border-radius:10px; height:8px; width:80px; display:inline-block; vertical-align:middle; overflow:hidden; margin-left:6px; border:1px solid rgba(255,255,255,0.1); }
    .wear-bar-fill  { height:100%; border-radius:10px; transition: width 0.6s ease-out; display:block; box-shadow: 0 0 8px rgba(255,255,255,0.3); }

    /* --- Spatial UI & Satellite Lock-on --- */
    .satellite-bg {
        position: absolute;
        inset: 0;
        z-index: 1;
        background-size: cover;
        background-position: center;
        transform: scale(1);
        animation: satellite-lock 0.8s ease-out forwards;
    }
    @keyframes satellite-lock {
        0%   { transform: scale(1.15); filter: blur(8px) brightness(1.5); }
        100% { transform: scale(1); filter: blur(0) brightness(1); }
    }
    
    /* Broadcast Ticker */
    .narrative-ticker {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        background: linear-gradient(90deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.8) 15%, rgba(0,0,0,0.8) 85%, rgba(0,0,0,0) 100%);
        color: #f0e6c0;
        font-size: 0.65em;
        font-weight: 600;
        padding: 3px 0;
        overflow: hidden;
        white-space: nowrap;
        z-index: 25;
        border-top: 1px solid rgba(255,215,100,0.2);
        letter-spacing: 0.5px;
        backdrop-filter: blur(4px);
    }
    .ticker-text {
        display: inline-block;
        padding-left: 100%;
        animation: ticker-anim 20s linear infinite;
    }
    @keyframes ticker-anim {
        0%   { transform: translate(0, 0); }
        100% { transform: translate(-100%, 0); }
    }

    /* Time of Day Overlays */
    .tod-overlay {
        position: absolute;
        inset: 0;
        z-index: 2;
        pointer-events: none;
    }
    .overlay-midday { background: transparent; }
    .overlay-evening { background: linear-gradient(135deg, rgba(255,140,0,0.15) 0%, transparent 100%); }
    .overlay-night { 
        background: transparent; 
    }
    .noise-grain {
        position: absolute;
        inset: 0;
        z-index: 3;
        opacity: 0.04;
        pointer-events: none;
        background: url('https://www.transparenttextures.com/patterns/black-thread.png'); /* fallback grain */
        animation: grain-shift 0.2s steps(2) infinite;
    }
    @keyframes grain-shift {
        0% { background-position: 0 0; }
        100% { background-position: 10% 10%; }
    }

    /* Filters */
    .filter-midday { filter: brightness(105%) contrast(110%); }
    .filter-evening { filter: sepia(40%) saturate(140%) hue-rotate(-20deg); }
    .filter-night { filter: brightness(75%) saturate(120%) sepia(10%) hue-rotate(190deg); }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); }
    ::-webkit-scrollbar-thumb { background: rgba(191, 148, 255, 0.3); border-radius: 3px; }

    .race-cards-scroll-container > div {
        display: contents;
    }

    /* Buttons as Cards */
    .stButton > button {
        background: none !important;
        border: none !important;
        padding: 0 !important;
        width: 100% !important;
        color: inherit !important;
        text-align: left !important;
    }

    /* Action Button Centering (Plus Button Only) */
    div[data-testid="column"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    div[data-testid="column"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton button {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        margin: 0 auto !important;
        width: 100% !important;
        min-width: 30px !important;
        height: 32px !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        opacity: 1 !important;
        padding: 0 !important;
    }
    div[data-testid="column"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton button p {
        margin: 0 !important;
        padding: 0 !important;
        text-align: center !important;
        width: 100% !important;
        line-height: 32px !important;
    }
    </style>
    <script>
    document.addEventListener('click', function(e) {
        if(e.target.tagName === 'BUTTON' || e.target.closest('button')) {
            let btn = e.target.closest('button');
            if(btn && btn.innerText.includes('GENERATE')) {
                let collapseBtn = document.querySelector('button[aria-label="Collapse sidebar"]');
                if(collapseBtn) {
                    setTimeout(() => collapseBtn.click(), 100);
                }
            }
        }
    });
    </script>
    """, unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data(file, mtime=None):
    df = pd.read_csv(file)
    df.fillna({'race_name': 'Unknown Race', 'race_special': ''}, inplace=True)
    return df

# --- Environment Engine ---
def get_season_for_hemisphere(month, lat):
    """Returns the local season based on month and hemisphere."""
    if -23.5 <= lat <= 23.5:
        return 'Tropical'
    north_season = {
        12: 'Winter', 1: 'Winter', 2: 'Winter',
        3: 'Spring', 4: 'Spring', 5: 'Spring',
        6: 'Summer', 7: 'Summer', 8: 'Summer',
        9: 'Autumn', 10: 'Autumn', 11: 'Autumn',
    }[month]
    if lat < -23.5:  # Southern hemisphere — flip season
        flip = {'Winter': 'Summer', 'Summer': 'Winter', 'Spring': 'Autumn', 'Autumn': 'Spring'}
        return flip[north_season]
    return north_season

def get_time_of_day(hour):
    if 8 <= hour < 16:
        return 'Midday'
    elif 16 <= hour < 19:
        return 'Evening'
    return 'Night'

def simulate_race_environment(lat, season, time_of_day):
    """Cascading probability simulation per the spec."""
    # Step A: Track Wear
    wear = random.choices(['Fresh', 'Used', 'Worn'], weights=[50, 35, 15])[0]

    # Step B: Weather
    weather_options = ['Fair', 'Cloudy', 'Rainy', 'Snowy']
    weather_weights = [60, 20, 15, 5]
    weather = random.choices(weather_options, weights=weather_weights)[0]
    if weather == 'Snowy' and season == 'Tropical':
        weather = 'Rainy'
    if weather == 'Snowy' and season not in ('Winter',):
        weather = random.choices(['Fair', 'Cloudy', 'Rainy'], weights=[60, 20, 20])[0]

    # Step C: Temperature
    if (season in ('Summer', 'Tropical')) and weather == 'Fair':
        temp = 'Hot'
    elif season == 'Winter' or (abs(lat) > 45 and weather in ('Rainy', 'Snowy')):
        temp = 'Cold'
    else:
        temp = 'Normal'

    # Step D: Ground Condition
    if weather in ('Fair', 'Cloudy'):
        if wear == 'Worn':
            ground = random.choices(['Firm', 'Good', 'Soft'], weights=[60, 25, 15])[0]
        else:
            ground = random.choices(['Firm', 'Good', 'Soft'], weights=[85, 10, 5])[0]
    else:  # Rainy or Snowy
        if wear == 'Fresh':
            ground = random.choices(['Soft', 'Heavy', 'Good'], weights=[55, 30, 15])[0]
        else:
            ground = random.choices(['Heavy', 'Soft'], weights=[60, 40])[0]

    return {'wear': wear, 'weather': weather, 'temp': temp, 'ground': ground}

def get_skill_tags(row, env):
    """Generate skill tags based on race data and environment."""
    tags = []
    tt = str(row.get('track_type', '')).lower()
    lt = str(row.get('length_type', ''))
    rank = str(row.get('race_rank', ''))
    continent = str(row.get('continent', ''))

    # Surface / Distance
    if 'turf' in tt: tags.append('Turf Specialist')
    elif 'dirt' in tt: tags.append('Dirt Specialist')
    else: tags.append('Synthetic Specialist')
    if lt: tags.append(f'{lt} Specialist')

    # Environment
    season = env.get('season', '')
    if season: tags.append(f'{season} Specialist')
    weather = env.get('weather', '')
    if weather: tags.append(f'{weather} Runner')
    ground = env.get('ground', '')
    if ground: tags.append(f'{ground} Ground Specialist')

    # Conditioning
    wear = env.get('wear', '')
    if wear: tags.append(f'{wear} Track Specialist')
    if env.get('temp') == 'Hot': tags.append('Heat Specialist')
    if env.get('temp') == 'Cold': tags.append('Winter Gal')

    # Time / Meta
    tod = env.get('time_of_day', '')
    if tod: tags.append(f'{tod} Specialist')
    if rank in ('1', '2', '3'): tags.append('Big Stage Specialist')
    if continent: tags.append(f'{continent} Specialist')

    return tags

def get_card_bg(rank):
    rank_str = str(rank)
    if rank_str == '1': return 'bg-1'
    if rank_str == '2': return 'bg-2'
    if rank_str == '3': return 'bg-3'
    if rank_str == '4': return 'bg-4'
    return 'bg-0'

def get_rank_badge(rank, is_major=False):
    rank_str = str(rank)
    if is_major: 
        return '<span class="badge metallic-badge">📡 MAJOR EVENT</span>'
    if rank_str == '1': return '<span class="badge metallic-badge">G1</span>'
    if rank_str == '2': return '<span class="badge badge-g2-metallic">G2</span>'
    if rank_str == '3': return '<span class="badge badge-g3-metallic">G3</span>'
    if rank_str == '4': return '<span class="badge badge-local">Local</span>'
    return '<span class="badge badge-none">Non-Graded</span>'

def get_track_badge(track_type):
    tt = str(track_type).lower()
    if 'turf' in tt: return '🌱 <span class="badge badge-turf">Turf</span>'
    if 'dirt' in tt: return '🟤 <span class="badge badge-dirt">Dirt</span>'
    return '⚙️ <span class="badge badge-synthetic">Synthetic</span>'

@st.cache_data
def get_country_flag(country_name):
    try:
        overrides = {'USA': 'US', 'UK': 'GB', 'United Kingdom': 'GB', 'UAE': 'AE', 'South Korea': 'KR', 'Vietnam': 'VN'}
        if country_name in overrides:
            code = overrides[country_name]
        else:
            country = pycountry.countries.search_fuzzy(country_name)[0]
            code = country.alpha_2
        return f'<img src="https://flagcdn.com/24x18/{code.lower()}.png" width="18" style="vertical-align: middle; margin-left: 4px; margin-bottom: 2px;">'
    except Exception:
        return "🏳️"

@st.cache_data
def get_country_flag_emoji(country_name):
    try:
        overrides = {'USA': 'US', 'UK': 'GB', 'United Kingdom': 'GB', 'UAE': 'AE', 'South Korea': 'KR', 'Vietnam': 'VN'}
        if country_name in overrides:
            code = overrides[country_name]
        else:
            country = pycountry.countries.search_fuzzy(country_name)[0]
            code = country.alpha_2
        # Convert country code to regional indicator symbols (emoji flags)
        return "".join(chr(127397 + ord(c)) for c in code.upper())
    except Exception:
        return "🏳️"

def render_pending_card():
    return '<div class="race-card" style="height:110px; opacity:0.3; display:flex; align-items:center; justify-content:center; border:1px dashed rgba(255,255,255,0.2); color:#aaa; font-style:italic;">🕒 PENDING...</div>'

def render_card_html(row, is_selected=False, is_active=False):
    sel_class = "race-card-selected" if is_selected else ""
    active_class = "race-card-active pulse-success" if is_active else ""
    rank_str = str(row.get('race_rank'))
    is_g1 = rank_str == '1'
    is_graded = rank_str in ('1', '2', '3')
    
    glow_class = "glow-g1" if is_g1 else ""
    # Shimmer for G1, G2, G3 using Neo-Modern Shimmer Streak
    shimmer_class = "shimmer-streak" if is_graded else ""
    
    # Add explicit rank-based left border to mini cards
    rank_border_colors = {
        '1': '#FFD700',   # G1 - Gold
        '2': '#C0C0C0',   # G2 - Silver
        '3': '#CD7F32',   # G3 - Bronze
        '4': '#0078D7',   # Local - Blue
    }
    border_color = rank_border_colors.get(rank_str, '#777777')  # Default Gray for Non-Graded
    rank_border = f"border-left: 5px solid {border_color};"
    
    html = f"""<div class="race-card {get_card_bg(row['race_rank'])} {sel_class} {active_class} {glow_class} {shimmer_class}" style="padding: 10px; min-height: 100px; border-bottom: none; border-radius: 12px 12px 0 0; margin-top: 5px; position:relative; {rank_border}"><div style="display:flex; justify-content:space-between; margin-bottom: 2px; position:relative; z-index:2;">{get_rank_badge(row['race_rank'], is_g1)}{get_track_badge(row['track_type'])}</div><div style="font-weight: 800; font-size: 0.85em; line-height: 1.1; margin: 2px 0; position:relative; z-index:2;">{row['race_name']}</div><div style="font-size: 0.7em; color: #ccc; position:relative; z-index:2;">📍 {row['racetrack']}, {row['country']} {get_country_flag(row['country'])}</div><div style="margin-top: 2px; font-size: 0.65em; opacity: 0.8; position:relative; z-index:2;">📏 {row['length']}m ({row['length_type']})</div></div>"""
    return html.strip()


def get_satellite_config_by_rank(race_rank):
    """
    Return satellite icon filename and radar ring color based on race rank.
    
    Args:
        race_rank: '1' (G1), '2' (G2), '3' (G3), '4' (Local), or '' (Non-graded)
    
    Returns:
        tuple: (icon_filename, ring_color_hex)
    """
    rank_str = str(race_rank).strip()
    
    rank_config = {
        '1': ('g1_satellite_icon.png', '#FFFF00'),      # Yellow
        '2': ('g2_satellite_icon.png', '#C0C0C0'),      # Silver Gray
        '3': ('g3_satellite_icon.png', '#CD7F32'),      # Brown
        '4': ('local_satellite_icon.png', '#0078D7'),   # Blue
    }
    
    return rank_config.get(rank_str, ('non_graded_satellite_icon.png', '#808080'))  # Gray for non-graded


def render_satellite_hud_map(highlighted_rows, selected_idx=0):
    import plotly.graph_objects as go
    import numpy as np

    if not highlighted_rows:
        return go.Figure().update_layout(template="plotly_dark", mapbox_style="dark")

    selected_row = highlighted_rows[selected_idx]
    slat, slon = selected_row['latitude'], selected_row['longitude']
    
    # Get icon and ring color based on race rank
    race_rank = selected_row.get('race_rank', '')
    sat_icon_filename, ring_color = get_satellite_config_by_rank(race_rank)

    fig = go.Figure()

    # 1. Path Lines
    if len(highlighted_rows) > 1:
        lats = [r['latitude'] for r in highlighted_rows]
        lons = [r['longitude'] for r in highlighted_rows]
        fig.add_trace(go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode='lines',
            line=dict(width=2, color='rgba(255, 255, 255, 0.4)'),
            hoverinfo='skip'
        ))

    # 2. Concentric Radar Rings (color based on race rank)
    for i in range(1, 5):
        pulse_size = 30 + (i * 35)
        pulse_size += np.sin(time.time() * 3) * 8
        pulse_opacity = max(0, 0.7 - (i * 0.15))
        fig.add_trace(go.Scattermapbox(
            lat=[slat],
            lon=[slon],
            mode='markers',
            marker=dict(
                size=pulse_size, 
                color=ring_color, 
                opacity=pulse_opacity, 
                symbol='circle'
            ),
            hoverinfo='skip'
        ))

    # 3. Satellite Icon Overlay (Paper-space center)
    sat_icon_b64 = get_base64_of_bin_file(sat_icon_filename)
    if sat_icon_b64:
        fig.add_layout_image(
            dict(
                source=f"data:image/png;base64,{sat_icon_b64}",
                xref="paper", yref="paper",
                x=0.5, y=0.56,
                sizex=0.15, sizey=0.15,
                xanchor="center", yanchor="middle",
                layer="above"
            )
        )

    fig.update_layout(
        mapbox=dict(
            style="white-bg",
            layers=[{
                "below": 'traces',
                "sourcetype": "raster",
                "sourceattribution": "Esri World Imagery",
                "source": ["https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"]
            }],
            center=dict(lat=slat, lon=slon),
            zoom=11
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=420,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def display_map_with_hud(placeholder, highlighted_rows, selected_idx):
    """Helper to render map + HUD overlays in a single placeholder."""
    mode = st.session_state.get('map_mode', "3D Tactical Globe")
    
    if mode == "Satellite HUD Map":
        fig = render_satellite_hud_map(highlighted_rows, selected_idx)
        # Combine Map + HUD into a single container-like structure using markdown for overlays
        with placeholder.container():
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            if highlighted_rows:
                target = highlighted_rows[selected_idx]
                # Scramble effect simulation
                scramble = str(random.randint(100, 999))
                st.markdown(f"""
                <div style="position:relative; margin-top:-420px; height:420px; pointer-events:none; z-index:100;">
                    <div style="position:absolute; top:15px; left:15px;">
                        <div class="hud-label">SAT_LINK: ONLINE</div>
                        <div class="hud-label">LAT: {target.get('latitude',0):.4f}{scramble}</div>
                        <div class="hud-label">LON: {target.get('longitude',0):.4f}{scramble}</div>
                        <div class="hud-label">TRACK_LOCK: {target.get('racetrack','').upper()}</div>
                    </div>
                    <div style="position:absolute; bottom:20px; right:20px; text-align:right;">
                        <div class="hud-label" style="font-size:0.7em; color:#00F2FF; text-shadow:none;">GEOSPATIAL_GRID_READY</div>
                        <div class="hud-label" style="font-size:0.6em; opacity:0.5; color:#00F2FF; text-shadow:none;">SIG_STRENGTH: 98%</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        fig = render_map(highlighted_rows, selected_idx)
        placeholder.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def render_map(highlighted_rows, selected_idx=0):
    import plotly.graph_objects as go
    fig = go.Figure()

    center_lat, center_lon = 20, 0
    zoom = 1

    if highlighted_rows:
        df_path = pd.DataFrame(highlighted_rows)
        # Add flag emoji for hover
        df_path['flag'] = df_path['country'].apply(get_country_flag_emoji)
        
        # 1. Lines connecting the points (No hover)
        if len(df_path) > 1:
            fig.add_trace(go.Scattergeo(
                lat=df_path['latitude'],
                lon=df_path['longitude'],
                mode='lines',
                line=dict(width=3, color='yellow', dash='dash'),
                hoverinfo='skip',
                showlegend=False
            ))

        # 2. Intermediate Markers (Yellow)
        if len(df_path) > 2:
            df_inter = df_path.iloc[1:-1]
            fig.add_trace(go.Scattergeo(
                lat=df_inter['latitude'],
                lon=df_inter['longitude'],
                mode='markers',
                marker=dict(size=10, color='yellow', symbol='circle'),
                hoverinfo='skip',
                showlegend=False
            ))
            
        # 3. Mark START (Green)
        fig.add_trace(go.Scattergeo(
            lat=[df_path['latitude'].iloc[0]],
            lon=[df_path['longitude'].iloc[0]],
            mode='markers+text',
            marker=dict(size=16, color='#00ff00', symbol='star'),
            text=["<b>START</b>"],
            textposition="top center",
            textfont=dict(color="#00ff00", size=14),
            hoverinfo='skip',
            showlegend=False
        ))
        
        # 4. Mark FINISH (Red)
        if len(df_path) > 1:
            fig.add_trace(go.Scattergeo(
                lat=[df_path['latitude'].iloc[-1]],
                lon=[df_path['longitude'].iloc[-1]],
                mode='markers+text',
                marker=dict(size=14, color='#ff3333', symbol='diamond'),
                text=["<b>FINISH</b>"],
                textposition="bottom center",
                textfont=dict(color="#ff3333", size=14),
                hoverinfo='skip',
                showlegend=False
            ))
            
        # 5. Selected Marker Highlight
        selected_row = df_path.iloc[selected_idx]
        fig.add_trace(go.Scattergeo(
            lat=[selected_row['latitude']],
            lon=[selected_row['longitude']],
            mode='markers',
            marker=dict(size=25, color='rgba(191, 148, 255, 0.4)', symbol='circle', line=dict(width=2, color='#bf94ff')),
            hoverinfo='skip',
            showlegend=False
        ))
            
        center_lat = selected_row['latitude']
        center_lon = selected_row['longitude']
        zoom = 3.5 # Focus on selected

    fig.update_layout(
        geo=dict(
            projection=dict(type="orthographic", rotation=dict(lat=center_lat, lon=center_lon), scale=2.4),
            showcoastlines=True, coastlinecolor="rgba(255, 255, 255, 0.4)",
            showland=True, landcolor="rgba(201, 209, 217, 0.9)",
            showocean=True, oceancolor="rgba(255, 255, 255, 0.04)",
            showcountries=True, countrycolor="rgba(255, 255, 255, 0.5)",
            bgcolor="rgba(0,0,0,0)",
            domain=dict(x=[0, 1], y=[0, 1])
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=420,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )
    return fig

def render_full_detail_card(row_data, env=None):
    if row_data is None: return
    if env is None: env = {}

    tt      = str(row_data['track_type']).lower()
    bg_file = 'turf_bg.png' if ('turf' in tt or 'synthetic' in tt) else 'dirt_bg.png'
    bg_base64 = get_base64_of_bin_file(bg_file)

    season  = env.get('season', '')
    weather = env.get('weather', '')
    temp    = env.get('temp', '')
    wear    = env.get('wear', '')
    ground  = env.get('ground', '')
    tod     = env.get('time_of_day', '')
    rank    = str(row_data.get('race_rank', ''))

    # ── 1. Spatial Background (spec §1, §4) ───────────────────────────────
    lat = row_data.get('latitude')
    lon = row_data.get('longitude')
    
    # Robust check for coordinates
    has_coords = False
    try:
        if lat is not None and lon is not None:
            # Ensure they are floats and not NaN
            lat_val, lon_val = float(lat), float(lon)
            if not (pd.isna(lat_val) or pd.isna(lon_val)):
                # Coordinates are valid if they aren't exactly 0,0 (unless actually at 0,0)
                if abs(lat_val) > 0.0001 or abs(lon_val) > 0.0001:
                    has_coords = True
    except (ValueError, TypeError):
        has_coords = False

    # ── 2. Time-of-Day Filters & Overlays (spec §2) ─────────────────────────
    tod_filter_class = f"filter-{tod.lower()}" if tod in ('Midday', 'Evening', 'Night') else ""
    tod_overlay_class = f"overlay-{tod.lower()}" if tod in ('Midday', 'Evening', 'Night') else ""
    noise_layer = '<div class="noise-grain"></div>' if tod == 'Night' else ""

    # Use Yandex Static Maps as a key-less satellite provider for demo purposes
    if has_coords:
        map_url = f"https://static-maps.yandex.ru/1.x/?ll={lon},{lat}&z=15&l=sat&size=650,350"
        bg_layer = f'<div class="satellite-bg {tod_filter_class}" style="background-image:url({map_url});"></div>'
    else:
        bg_layer = f'<div class="satellite-bg {tod_filter_class}" style="background-image:url(\'data:image/png;base64,{bg_base64}\');"></div>'
    
    # Gradient overlay to ensure readability
    grad_overlay = '<div style="position:absolute;inset:0;z-index:4;background:linear-gradient(90deg,rgba(0,0,0,0.85) 0%,rgba(0,0,0,0.3) 100%);"></div>'

    bg_style = f"background-color:#111;" # Container base

    # ── 1b. Text Color Contrast ───────────────────────────────────────────
    season_colors = {
        'Spring': '#1a1a1a', 'Summer': '#ffffff', 'Autumn': '#ffffff',
        'Winter': '#1a1a1a', 'Tropical': '#ffffff'
    }
    text_color = season_colors.get(season, '#ffffff')

    # ── 2. Particle overlay HTML ────────────────────────────────────────────
    particles = ''
    # ── 2b. Summer particle: bokeh + lens flare (replaces heat haze) ────────
    if season == 'Spring':
        particles = '<div class="particle-layer">' + ''.join('<div class="petal"></div>'*5) + '</div>'
    elif season == 'Summer':
        bokeh_divs = ''.join('<div class="bokeh-circle"></div>'*5)
        lens_flare = ('<svg class="lens-flare" width="80" height="80" viewBox="0 0 80 80">'
                      '<circle cx="40" cy="40" r="18" fill="rgba(255,240,180,0.35)"/>'
                      '<circle cx="40" cy="40" r="8" fill="rgba(255,255,220,0.6)"/>'
                      '<line x1="40" y1="5" x2="40" y2="75" stroke="rgba(255,230,100,0.18)" stroke-width="2"/>'
                      '<line x1="5" y1="40" x2="75" y2="40" stroke="rgba(255,230,100,0.18)" stroke-width="2"/>'
                      '<line x1="15" y1="15" x2="65" y2="65" stroke="rgba(255,230,100,0.12)" stroke-width="1.5"/>'
                      '<line x1="65" y1="15" x2="15" y2="65" stroke="rgba(255,230,100,0.12)" stroke-width="1.5"/>'
                      '</svg>')
        particles = f'<div class="particle-layer">{bokeh_divs}{lens_flare}</div>'
    elif season == 'Autumn':
        particles = '<div class="particle-layer">' + ''.join('<div class="leaf"></div>'*4) + '</div>'
    elif season == 'Winter' and weather == 'Snowy':
        particles = '<div class="particle-layer">' + ''.join('<div class="snowflake"></div>'*5) + '</div>'
    if weather in ('Rainy', 'Snowy') and season != 'Winter':
        particles = '<div class="particle-layer">' + ''.join('<div class="rain-streak"></div>'*6) + '</div>'
    elif weather == 'Rainy':
        particles += '<div class="particle-layer">' + ''.join('<div class="rain-streak"></div>'*6) + '</div>'

    # ── 3. Condition Glow class (spec §4) ───────────────────────────────────
    glow_class = ''
    if rank == '1':
        glow_class = 'glow-gold'
    elif tod == 'Night':
        glow_class = 'glow-night'
    elif weather in ('Rainy', 'Snowy') and ground == 'Heavy':
        glow_class = 'glow-storm'

    # ── 4. Wear progress bar (spec §5) ──────────────────────────────────────
    wear_pct  = {'Fresh': 80, 'Used': 50, 'Worn': 25}.get(wear, 0)
    wear_col  = {'Fresh': '#00ff00', 'Used': '#ffff00', 'Worn': '#ff0000'}.get(wear, '#aaa')
    wear_bar  = (
        f'<div class="wear-bar-track"><div class="wear-bar-fill" style="width:{wear_pct}%;background:{wear_col};"></div></div>'
    )

    # ── 3b. Ground texture badge (spec §3) ───────────────────────────────────
    ground_tex = {'Firm':'🌿 Firm','Good':'🟢 Good','Soft':'💧 Soft','Heavy':'🟫 Heavy'}.get(ground, ground)
    ground_col = {'Firm':'#27ae60','Good':'#5dade2','Soft':'#a29bfe','Heavy':'#5D4037'}.get(ground,'#aaa')

    # ── Ribbon ───────────────────────────────────────────────────────────────
    weather_icon = {'Fair':'☀️','Cloudy':'☁️','Rainy':'🌧️','Snowy':'❄️'}.get(weather,'❓')
    temp_col_map = {'Hot':'#ff6b6b','Cold':'#74b9ff','Normal':'#ccc'}
    temp_color   = temp_col_map.get(temp, '#ccc')
    tod_icon     = {'Midday':'☀️🕛','Evening':'🌆🕔','Night':'🌙🕗'}.get(tod,'🕒')
    temp_glow = {'Hot': '0 0 8px rgba(255,80,0,0.9), 0 0 16px rgba(255,50,0,0.5)', 'Cold': '0 0 8px rgba(80,180,255,0.9), 0 0 16px rgba(60,140,255,0.5)'}.get(temp, 'none')
    ribbon = ''
    if env:
        ribbon = (
            f'<div style="display:flex;gap:15px;margin-bottom:10px;padding:5px 10px;background:rgba(0,0,0,0.4);border-radius:8px;align-items:center;flex-wrap:wrap;font-size:0.82em;text-shadow:0 1px 3px rgba(0,0,0,0.9);color:#ffffff;">'
            f'<span>{weather_icon} <b>{weather}</b></span>'
            f'<span>🌡️ <span style="color:{temp_color};font-weight:700;text-shadow:{temp_glow};">{temp}</span></span>'
            f'<span>{tod_icon} {tod}</span>'
            f'<span style="display:flex;align-items:center;gap:6px;">🏗️ {wear} {wear_bar} <span style="color:{ground_col};font-weight:700;margin-left:4px;">{ground_tex}</span></span>'
            f'</div>'
        )

    # ── Skill Tags ────────────────────────────────────────────────────────────
    skill_tags = get_skill_tags(row_data, env) if env else []
    tag_style  = 'background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.3);color:#fff;font-size:0.58em;font-weight:700;padding:2px 7px;border-radius:20px;white-space:nowrap;'
    tags_html  = ''
    if skill_tags:
        tags_html = '<div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:6px;">' + ''.join(f'<span style="{tag_style}">{t}</span>' for t in skill_tags) + '</div>'

    # ── Badges / Meta ─────────────────────────────────────────────────────────
    season_badge = f'<span style="font-size:0.75em;font-weight:700;background:rgba(255,255,255,0.2);border:1px solid rgba(255,255,255,0.4);padding:2px 8px;border-radius:4px;margin-left:4px;color:#ffffff;text-shadow:0 1px 2px rgba(0,0,0,0.5);display:inline-flex;align-items:center;gap:4px;">📅 {season}</span>' if season else ''
    flag_html    = get_country_flag(row_data['country'])
    rank_badge   = get_rank_badge(row_data['race_rank'])
    track_badge  = get_track_badge(row_data['track_type'])

    # ────────────────────────────────────────────────────────────────────────
    # ── MODULAR NARRATIVE ENGINE: All Narrative Layers (Master v1.6) ────────
    # ────────────────────────────────────────────────────────────────────────
    
    # LAYER 1: Umamusume Tactical Layer [UMA_TAC] - Track-specific tactical hints
    uma_tac_map = {
        'Kyoto': "The Hill of Kyoto awaits. Conserve your stamina for the descent, or watch the leaders vanish before the final straight.",
        'Nakayama': "The final slope at Nakayama is a 'Stamina Killer.' Without a strong 'Power' rating, the rise will be insurmountable.",
        'Hanshin': "Beware the Hanshin final corner. It's a test of 'Guts' as the incline begins right when the legs are heaviest.",
        'Tokyo': "The Garden of Dreams. This massive straight is built for those with top-tier 'Acceleration' skills to burn.",
        'Niigata': "The longest straight in the circuit. There's nowhere to hide here—pure speed and 'Top Gear' are the only paths to victory.",
        'Ooi': "The Twinkle Race environment under the lights. The 'Dirt' expertise here separates the legends from the field.",
        'Longchamp': "The target of every 'L'Arc' dream. The false straight will deceive the impatient; only a true Ace finds the line here.",
        'Del Mar': "Where the turf meets the surf - the salt air of Del Mar provides a refreshing backdrop for this high-stakes sprint.",
        'Santa Anita': "The American dirt challenge. High-intensity 'Early Game' skills are required to secure the front in this fast-paced arena.",
        'Churchill Downs': "Beneath the Twin Spires, the ghosts of past champions watch as the next chapter of American dirt history is written."
    }
    
    # LAYER 2: Umamusume Character Resonance [UMA_CHAR] - Horse personality types
    uma_char_map = {
        'long_distance': "The spirit of the eccentric champion looms over this distance. Expect the unexpected—the 'long-range' move could start at any moment.",
        'stamina_grit': "A grueling test of resolve. This track demands the 'unyielding heart' that defines the greatest comeback stories.",
        'speed_front': "The scenery ahead belongs only to the fastest. A clear lead is the only way to silence the chasing pack today.",
        'versatile_dirt': "From turf to dirt, a true 'multi-talent' spirit is required to conquer this versatile surface."
    }
    
    # LAYER 3: Elite Track Tactical Hooks [ELITE_TAC] - High-fidelity track-specific
    elite_tac_map = {
        'Chantilly': "Racing against the backdrop of the Château; the elegance of Chantilly hides the brutal demand of its uphill finish.",
        'Deauville': "The sea breeze off the English Channel whistles through the stands as we prepare for a showdown on the Normandy coast.",
        'Saint-Cloud': "Elevated and taxing, Saint-Cloud demands a horse with a massive heart and an even bigger stride.",
        'Belmont Park': "The 'Big Sandy' - Belmont's massive oval - will expose any flaw in stamina today. This is where the long-winded thrive.",
        'Santa Anita': "In the shadow of the San Gabriel Mountains, the high-speed drama of California racing begins."
    }
    
    # LAYER 4: Special Event Logic [EVENT_HOOK] - Breeders' Cup and special series
    event_hook_map = {
        'Breeders Cup': "The world's stage is set. We have reached the Breeders' Cup—where the best from every continent collide to crown the ultimate champion."
    }
    
    # LAYER 5: Continental Atmospheric Modules [CON_ATM]
    continental_atm = {
        'Africa': {
            'hook': "The golden sun of the savanna casts long shadows over the track as we arrive in Africa.",
            'bridge': "Stamina and heart are the requirements for success on this vibrant, rising circuit."
        },
        'Asia': {
            'hook': "The neon pulse of the East sets the stage for today's contest.",
            'bridge': "Amidst the high-tech precision of the Asian circuit, the air is thick with expectation."
        },
        'Europe': {
            'hook': "Deep in the heart of the continent where racing history was written...",
            'bridge': "Tradition meets the modern turf as we prepare for another classic European battle."
        },
        'North America': {
            'hook': "The vast arenas of North America provide a grand stage for today's speed-demons.",
            'bridge': "From the dirt tracks of the heartland to the coastal cathedrals, the pace is relentless."
        },
        'South America': {
            'hook': "Passion and flair define the southern circuit as we head to South America.",
            'bridge': "The vibrant energy of the crowd is mirrored in the fierce competition on the track."
        },
        'Oceania': {
            'hook': "The southern cross shines bright over the expansive fields of the Oceania circuit.",
            'bridge': "Fresh coastal winds challenge the stamina of the field in this island-continent clash."
        }
    }
    
    # LAYER 6: Country-Specific Tactical Hooks [CTR_TAC]
    country_tac_map = {
        'Japan': "The precision of the Japanese turf demands absolute synchronization between horse and rider.",
        'Australia': "A grueling test under the vast southern sky; only the hardiest sprinters thrive in the Australian heat.",
        'USA': "It's a power-game today on the heavy-hitting American dirt; speed is the only language spoken here.",
        'UK': "Undulating terrain and unpredictable skies—this is the ultimate test of European tactical versatility.",
        'South Africa': "The storied turf of the Southern Tip offers no easy victories today; only the bravest will conquer the Drakensberg winds.",
        'Argentina': "A rhythmic, high-tempo affair as we've come to expect from the legendary Argentinian breeders."
    }
    
    # LAYER 7: Enhanced Time-of-Day Environmental [TOD_ENV]
    tod_env_map = {
        'Morning': "The crisp morning air carries the scent of fresh-cut grass and pure potential.",
        'Noon': "Under the high, unforgiving midday sun, every bead of sweat and every stride counts.",
        'Evening': "As the sky bleeds into twilight, the floodlights illuminate the path to glory.",
        'Night': "The cool night air hums with electricity; under the stars, legends are whispered before they are made."
    }
    
    # LAYER 8: Extreme Regional Weather [WEA_EXT]
    weather_extreme_map = {
        ('Africa', 'Hot'): "The shimmering heat haze rises from the savanna, turning the track into a gauntlet of pure endurance.",
        ('Asia', 'Rainy'): "A wall of water descends upon the neon-lit circuit, transforming the turf into a treacherous, rain-slicked mirror.",
        ('Europe', 'Cloudy'): "A thick continental mist clings to the historical grounds, hiding the far turn from view and testing the jockeys' instincts.",
        ('North America', 'Windy'): "Swirling grit from the American plains sweeps across the dirt, stinging the eyes and choking the lungs of the chasing pack.",
        ('Oceania', 'Rainy'): "Brutal winds off the Pacific buffet the field, turning the home stretch into a desperate battle against the elements."
    }
    
    # LAYER 9: Library Hooks [LIB_HOOK] - Series and collection context
    library_hook_map = {
        'Triple Crown': "The atmosphere is suffocating; we are in the heart of the Triple Series where every point counts toward immortality.",
        'Triple Series': "The atmosphere is suffocating; we are in the heart of the Triple Series where every point counts toward immortality.",
        'The Stable': "A familiar face from the archives. This library favorite returns to the spotlight under the Race Director's command."
    }
    
    # Helper function to get narrative layer
    def get_narrative_layer(layer_type, key, default=""):
        layer_maps = {
            'uma_tac': uma_tac_map,
            'elite_tac': elite_tac_map,
            'event_hook': event_hook_map,
            'country_tac': country_tac_map,
            'tod_env': tod_env_map,
            'library_hook': library_hook_map
        }
        return layer_maps.get(layer_type, {}).get(key, default)

    # ── Narrative Summary Engine (spec §2) ─────────────────────────────────
    # MODULAR NARRATIVE ASSEMBLY: Master v1.6
    race_name = row_data["race_name"]
    tt_lower  = tt  # already computed above
    racetrack = row_data.get('racetrack', '')
    country = row_data.get('country', '')
    continent = row_data.get('continent', '')
    
    # Try to assemble narrative from modular layers:
    # Priority: [EVENT_HOOK or UMA_CHAR or LIB_HOOK] + [UMA_TAC or ELITE_TAC or CTR_TAC or CON_ATM] + [TOD_ENV or WEA_EXT]
    
    narrative_segments = []
    
    # --- Check for Special Event Hook (Breeder's Cup) ---
    if 'Breeder' in race_name or 'Breeders' in race_name:
        narrative_segments.append(get_narrative_layer('event_hook', 'Breeders Cup'))
    
    # --- Check for Track-Specific Tactical (UMA_TAC or ELITE_TAC) ---
    uma_tac = get_narrative_layer('uma_tac', racetrack)
    elite_tac = get_narrative_layer('elite_tac', racetrack)
    country_tac = get_narrative_layer('country_tac', country)
    
    if uma_tac:
        narrative_segments.append(uma_tac)
    elif elite_tac:
        narrative_segments.append(elite_tac)
    elif country_tac:
        narrative_segments.append(country_tac)
    else:
        # Fallback to continental atmospheric
        cont_atm = continental_atm.get(continent, {})
        if cont_atm:
            narrative_segments.append(random.choice([cont_atm.get('hook', ''), cont_atm.get('bridge', '')]))
    
    # --- Check for Time-of-Day Environmental or Extreme Weather ---
    weather_extreme_key = (continent, temp) if temp else (continent, weather)
    wea_ext = weather_extreme_map.get(weather_extreme_key)
    if wea_ext:
        narrative_segments.append(wea_ext)
    else:
        # Fallback to TOD environment
        tod_env_text = get_narrative_layer('tod_env', tod)
        if tod_env_text:
            narrative_segments.append(tod_env_text)
    
    # If we have assembled narrative from new layers, use it; otherwise fall back to v5 system
    if narrative_segments and len(narrative_segments) >= 2:
        narrative = ' '.join(filter(None, narrative_segments[:2]))
    else:
        # ── Narrative Summary Engine (Modular v5 - Fallback) ────────────────
        # Segment 1: The Hook (Categorized by Rank)
        rank_str = str(rank)
        hooks = []
        if rank_str == '1':
            hooks = [
                f"The legendary {race_name} takes center stage,",
                f"History is in the making as the giants gather for the {race_name},",
                f"The pinnacle of the season has arrived: the prestigious {race_name},",
                f"The atmosphere is electric for today's crown jewel, the {race_name},",
                f"Immortal glory awaits the victor of the {race_name},"
            ]
        elif rank_str in ('2', '3'):
            hooks = [
                f"Anticipation reaches a fever pitch for the {race_name},",
                f"Crucial points and pride are on the line in the {race_name},",
                f"The field looks to secure their legacy in the competitive {race_name},",
                f"A high-stakes stepping stone unfolds today in the {race_name},",
                f"Tension mounts as the contenders line up for the {race_name},"
            ]
        else:
            hooks = [
                f"A spirited battle is expected for the {race_name},",
                f"Local favorites look to make their mark in the {race_name},",
                f"The journey begins here with the hard-fought {race_name},",
                f"Fresh faces and local legends collide in the {race_name},",
                f"An unpredictable 'Prelude' kicks off with the {race_name},"
            ]
        hook = random.choice(hooks)
        
        # Segment 2: The Atmospheric Bridge (Time & Weather)
        bridge = ""
        w_low = weather.lower()
        if tod == 'Night':
            options = [
                f"illuminated by the steady glow of floodlights under a {w_low} sky.",
                f"as the cool evening air settles over a {w_low} course.",
                f"shimmering under the artificial lights during this {w_low} night session.",
                f"with the moon hanging low over these {w_low} conditions."
            ]
            bridge = random.choice(options)
        elif tod == 'Evening':
            options = [
                f"racing into the fading golden twilight of a {w_low} afternoon.",
                f"as the sun dips below the horizon, casting an amber glow over this {w_low} meet.",
                f"during the transition to dusk, with {w_low} conditions framing the view."
            ]
            bridge = random.choice(options)
        else: # Midday
            options = [
                f"braving the intense, unfiltered heat of a {w_low} afternoon.",
                f"with maximum visibility and the sun directly overhead on this {w_low} day.",
                f"as a bright {w_low} sky provides a brilliant backdrop for the action.",
                f"under a relentless sun that is testing the limits of this {w_low} session."
            ]
            bridge = random.choice(options)
            
        # Segment 3: Tactical Outlook (Ground & Distance)
        tactical = ""
        lt = row_data.get('length_type', '')
        if ground == 'Firm' and lt == 'Sprint':
            options = [
                "where the speed kings will find a lightning-fast surface for their opening burst.",
                "rewarding those with the raw explosive power to conquer the clock.",
                "guaranteeing a heart-pounding dash where every split-second is vital."
            ]
            tactical = random.choice(options)
        elif ground == 'Heavy' and lt == 'Long':
            options = [
                "becoming a punishing war of attrition on a surface that will swallow the weak.",
                "demanding every ounce of stamina as the mud turns the final straight into a slog.",
                "where only the grittiest stayers will endure this grueling test of willpower."
            ]
            tactical = random.choice(options)
        elif ground == 'Good' and lt == 'Mile':
            options = [
                "offering a balanced, tactical stage for the milers to find their rhythm.",
                "setting the scene for a clean contest of speed, timing, and positioning.",
                "where the turf is just right for a display of pure, high-class athleticism."
            ]
            tactical = random.choice(options)
        elif wear == 'Worn':
            options = [
                "on a degraded track where the 'inside rail' has become a treacherous gamble.",
                "where navigating the rough patches is as important as the horse's speed.",
                "on a surface that is clearly showing its age, favoring the clever tacticians."
            ]
            tactical = random.choice(options)
        elif wear == 'Fresh' and 'turf' in tt.lower():
            tactical = "on a pristine carpet of grass that promises a clean, high-speed contest."
        elif ground == 'Soft' and lt == 'Medium':
            tactical = "where the give in the ground will favor the powerful, heavy-striding stayers."
        elif 'dirt' in tt.lower() and temp == 'Hot' and weather != 'Snowy':
            tactical = "where the rising dust and scorching sand will blast the resolve of the field."
        elif weather == 'Snowy' and (season == 'Winter' or season != 'Tropical'):
            tactical = "as the field hunts for traction on a surface that has become a silent, frozen theater."
        else:
            tactical = "as the field prepares for a high-stakes tactical contest under these unique local parameters."
            
        narrative = f"{hook} {bridge} {tactical}"

    narrative_html = ''
    if narrative:
        narrative_html = (f'<div class="narrative-ticker">'
                          f'<div class="ticker-text">🎙️ LIVE COMMENTARY: {narrative} &nbsp;&nbsp; • &nbsp;&nbsp; 🎙️ LIVE COMMENTARY: {narrative}</div>'
                          f'</div>')

    # ── Assemble ──────────────────────────────────────────────────────────────
    html = (
        f'<div class="full-detail-card {get_card_bg(rank)} {glow_class}" style="{bg_style}">'
        f'{bg_layer}'
        f'<div class="{tod_overlay_class}"></div>'
        f'{noise_layer}'
        f'{grad_overlay}'
        f'{particles}'
        f'{narrative_html}'
        f'<div class="full-detail-content" style="color:{text_color};padding-bottom:15px;">'
        f'<div style="flex:1;">'
        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">{rank_badge}{track_badge}{season_badge}</div>'
        f'{ribbon}'
        f'<div style="font-size:1.45em;font-weight:900;color:#fff;line-height:1;margin-bottom:5px;letter-spacing:-0.5px;text-shadow:0 1px 6px rgba(0,0,0,0.8);">{row_data["race_name"]}</div>'
        f'<div style="font-size:0.95em;color:#fff;font-weight:600;display:flex;align-items:center;gap:6px;text-shadow:0 1px 4px rgba(0,0,0,0.7);">'
        f'<span>📍 {row_data["racetrack"]}</span>'
        f'<span style="margin-left:24px;font-weight:400;color:#ddd;display:flex;align-items:center;gap:4px;">{row_data["country"]} {flag_html}</span>'
        f'</div>'
        f'{tags_html}'
        f'</div>'
        f'<div style="text-align:right;background:rgba(0,0,0,0.55);padding:10px 14px;border-radius:10px;border:1px solid rgba(255,255,255,0.2);min-width:105px;backdrop-filter:blur(6px);flex-shrink:0;">'
        f'<div style="color:#bf94ff;font-size:0.65em;text-transform:uppercase;letter-spacing:2px;font-weight:800;margin-bottom:2px;">DISTANCE</div>'
        f'<div style="font-size:1.5em;font-weight:900;color:#fff;line-height:1;">{row_data["length"]}m</div>'
        f'<div style="color:#bbb;font-size:0.78em;font-weight:600;">{row_data["length_type"]}</div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

def get_card_bg(rank):
    rank_str = str(rank)
    if rank_str == '1': return 'bg-1'
    if rank_str == '2': return 'bg-2'
    if rank_str == '3': return 'bg-3'
    if rank_str == '4': return 'bg-4'
    return 'bg-0'

def format_race_name(name):
    # If generic concatenation
    if name.startswith('JRA ') or name.startswith('NAR ') or ('m Turf' in name) or ('m Dirt' in name):
        return f'<span class="race-name-generic">{name}</span>'
    return f'<span class="race-name-official">{name}</span>'

def export_pdf(races_df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Horse Racing Racetrack Randomizer - Results", ln=1, align='C')
    pdf.ln(10)
    for idx, row in races_df.iterrows():
        text = f"{idx+1}. {row['race_name']} - {row['racetrack']}, {row['country']} | {row['length']}m ({row['length_type']}) | {row['track_type']}"
        # FPDF has issues with unicode/emojis in default font, so we use ascii-safe text
        pdf.cell(200, 10, txt=text.encode('latin-1', 'replace').decode('latin-1'), ln=1)
    return bytes(pdf.output())

def save_user_groups(groups):
    with open('user_groups.json', 'w', encoding='utf-8') as f:
        json.dump(groups, f, indent=4, ensure_ascii=False)

def sync_user_groups_with_csv(df, current_groups):
    """Dynamically adds missing race_special groupings from CSV to the user's stable."""
    if 'race_special' not in df.columns:
        return current_groups, False
    
    changed = False
    # Filter rows with special tags
    specials = df[df['race_special'].notna() & (df['race_special'] != '')]
    grouped = specials.groupby('race_special')
    
    for name, group in grouped:
        if name not in current_groups:
            # Add new discovered library
            current_groups[name] = group.to_dict('records')
            changed = True
            
    if changed:
        # Alphabetical Sort
        current_groups = dict(sorted(current_groups.items()))
        
    return current_groups, changed

# --- Main App ---
def main():
    inject_css()
    st.title("🏇 Horse Racing Racetrack Randomizer")
    
    # Session State Initialization
    if 'generated_races' not in st.session_state:
        st.session_state.generated_races = pd.DataFrame()
    if 'selected_race_idx' not in st.session_state:
        st.session_state.selected_race_idx = 0
    if 'race_environments' not in st.session_state:
        st.session_state.race_environments = {}
    if 'gen_id' not in st.session_state:
        st.session_state.gen_id = 0
    if 'director_mode' not in st.session_state:
        st.session_state.director_mode = False
    if 'director_slots' not in st.session_state:
        st.session_state.director_slots = [
            {'race_name': None, 'racetrack': None, 'length': None, 'rank': 'Auto', 'weather': 'Auto', 'ground': 'Auto', 'time': 'Auto'} for _ in range(5)
        ]
    if 'user_groups' not in st.session_state:
        if os.path.exists('user_groups.json'):
            with open('user_groups.json', 'r', encoding='utf-8') as f:
                st.session_state.user_groups = json.load(f)
        else:
            st.session_state.user_groups = {"Default": []}
        
    if 'last_deleted_group' not in st.session_state:
        st.session_state.last_deleted_group = None
    if 'selected_stable_race' not in st.session_state:
        st.session_state.selected_stable_race = None
    if 'last_deleted_name' not in st.session_state:
        st.session_state.last_deleted_name = None
            
    # File Uploader
    with st.sidebar.expander("📁 Data Source", expanded=False):
        uploaded_file = st.file_uploader("Upload new racetrack.csv", type=['csv'])
        if uploaded_file is not None:
            df = load_data(uploaded_file)
            st.success("Custom data loaded!")
        else:
            try:
                mtime = os.path.getmtime('racetrack.csv')
                df = load_data('racetrack.csv', mtime)
            except FileNotFoundError:
                st.error("racetrack.csv not found in the current directory. Please upload one.")
                st.stop()
                
        st.write(f"Total races available: {len(df)}")

    # Dynamic Sync Stable with CSV
    st.session_state.user_groups, has_synced = sync_user_groups_with_csv(df, st.session_state.user_groups)
    if has_synced:
        save_user_groups(st.session_state.user_groups)
        st.toast("✨ New Series discovered in database!")

    # Race Director Toggle
    st.session_state.director_mode = st.sidebar.toggle("🛠️ Race Director Mode", value=st.session_state.director_mode, help="Enable manual slot management and smart filler logic.")

    # --- Environment / Time Controls ---
    now = datetime.now()
    with st.sidebar.expander("🌤️ Race Environment", expanded=False):
        auto_detect = st.toggle("Auto-detect time & month", value=True)
        if auto_detect:
            current_month = now.month
            current_hour  = now.hour
            st.caption(f"🕒 Detected: {now.strftime('%B')} | {now.strftime('%H:%M')}")
        else:
            month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
            current_month = st.select_slider("Month", options=list(range(1,13)), value=now.month,
                                              format_func=lambda x: month_names[x-1])
            current_hour  = st.slider("Hour of Day (24h)", 0, 23, now.hour)

    time_of_day = get_time_of_day(current_hour)

    # --- The Stable (Persistent Storage) ---
    with st.sidebar.expander("🐎 The Stable (Libraries)", expanded=False):
        libs = sorted(list(st.session_state.user_groups.keys()))
        if "Default" in libs:
            libs.remove("Default")
            libs = ["Default"] + libs
        active_lib = st.selectbox("Library", options=libs)
        
        # UI: Buttons in a row
        bcol1, bcol2 = st.columns(2)
        new_lib_name = bcol1.text_input("New Name", label_visibility="collapsed", placeholder="New Library Name")
        if bcol1.button("✨ CREATE", key="create_lib_btn", use_container_width=True):
            if new_lib_name and new_lib_name not in st.session_state.user_groups:
                st.session_state.user_groups[new_lib_name] = []
                # Sort alphabetically
                st.session_state.user_groups = dict(sorted(st.session_state.user_groups.items()))
                save_user_groups(st.session_state.user_groups)
                st.rerun()
        
        if active_lib != "Default":
            if bcol2.button("🗑️ DELETE", key=f"del_lib_{active_lib}", use_container_width=True):
                st.session_state.last_deleted_name = active_lib
                st.session_state.last_deleted_group = st.session_state.user_groups[active_lib]
                del st.session_state.user_groups[active_lib]
                save_user_groups(st.session_state.user_groups)
                st.rerun()
        
        if st.session_state.last_deleted_name:
            if st.button(f"↩️ UNDO Delete ({st.session_state.last_deleted_name})", key="undo_delete_lib", use_container_width=True):
                st.session_state.user_groups[st.session_state.last_deleted_name] = st.session_state.last_deleted_group
                st.session_state.last_deleted_name = None
                st.session_state.last_deleted_group = None
                save_user_groups(st.session_state.user_groups)
                st.rerun()

        st.markdown("---")
        for idx_lib, race_lib in enumerate(st.session_state.user_groups[active_lib]):
            # Unique ID for active check: Name + Racetrack + Length
            lib_uid = f"{race_lib['race_name']}_{race_lib['racetrack']}_{race_lib['length']}"
            held_uid = f"{st.session_state.selected_stable_race['race_name']}_{st.session_state.selected_stable_race['racetrack']}_{st.session_state.selected_stable_race['length']}" if st.session_state.selected_stable_race else ""
            
            is_active = (lib_uid == held_uid)
            st.markdown(render_card_html(race_lib, is_active=is_active), unsafe_allow_html=True)
            
            c_lib1, c_lib2, c_lib3, c_lib4 = st.columns([2, 1, 1, 1])
            
            label_select = "✅ SELECTED" if is_active else "📍 PICKUP"
            if c_lib1.button(label_select, key=f"sel_lib_{active_lib}_{idx_lib}", use_container_width=True):
                if is_active:
                    st.session_state.selected_stable_race = None
                else:
                    st.session_state.selected_stable_race = race_lib
                st.rerun()
            if c_lib2.button("↑", key=f"up_{active_lib}_{idx_lib}") and idx_lib > 0:
                st.session_state.user_groups[active_lib][idx_lib], st.session_state.user_groups[active_lib][idx_lib-1] = \
                    st.session_state.user_groups[active_lib][idx_lib-1], st.session_state.user_groups[active_lib][idx_lib]
                save_user_groups(st.session_state.user_groups)
                st.rerun()
            if c_lib3.button("↓", key=f"down_{active_lib}_{idx_lib}") and idx_lib < len(st.session_state.user_groups[active_lib])-1:
                st.session_state.user_groups[active_lib][idx_lib], st.session_state.user_groups[active_lib][idx_lib+1] = \
                    st.session_state.user_groups[active_lib][idx_lib+1], st.session_state.user_groups[active_lib][idx_lib]
                save_user_groups(st.session_state.user_groups)
                st.rerun()
            if c_lib4.button("❌", key=f"del_stable_{active_lib}_{idx_lib}"):
                st.session_state.user_groups[active_lib].pop(idx_lib)
                save_user_groups(st.session_state.user_groups)
                st.rerun()
            
        st.markdown("---")
        if st.button("📥 Load Library to Director", key=f"load_lib_{active_lib}", help="Auto-fill slots with this library."):
            for i_l, r_l in enumerate(st.session_state.user_groups[active_lib]):
                if i_l < 5:
                    st.session_state.director_slots[i_l]['race_name'] = r_l['race_name']
                    st.session_state.director_slots[i_l]['racetrack'] = r_l['racetrack']
                    st.session_state.director_slots[i_l]['length'] = r_l['length']
            st.rerun()
        else:
            st.caption("Empty Library")

        
    # Sidebar Filters
    # Sidebar Map Mode
    st.sidebar.header("🗺️ Display Settings")
    map_mode = st.sidebar.selectbox("Map Visualization", ["3D Tactical Globe", "Satellite HUD Map"])
    st.session_state.map_mode = map_mode
    
    st.sidebar.markdown("---")
    st.sidebar.header("🎯 Global Filters")
    
    col1, col2 = st.sidebar.columns(2)
    continents = col1.multiselect("Continent", options=sorted(df['continent'].unique().tolist()))
    if continents:
        df_filtered = df[df['continent'].isin(continents)]
    else:
        df_filtered = df.copy()
        
    countries = col2.multiselect("Country", options=sorted(df_filtered['country'].unique().tolist()))
    if countries:
        df_filtered = df_filtered[df_filtered['country'].isin(countries)]
        
    racecourses = st.sidebar.multiselect("Racecourse", options=sorted(df_filtered['racetrack'].unique().tolist()))
    if racecourses:
        df_filtered = df_filtered[df_filtered['racetrack'].isin(racecourses)]
        
    organizers = st.sidebar.multiselect("Organizer", options=sorted(df_filtered['organizer'].dropna().unique().tolist()))
    if organizers:
        df_filtered = df_filtered[df_filtered['organizer'].isin(organizers)]
        
    col3, col4 = st.sidebar.columns(2)
    length_types = col3.multiselect("Length Type", options=df['length_type'].unique().tolist())
    if length_types:
        df_filtered = df_filtered[df_filtered['length_type'].isin(length_types)]
        
    track_types = col4.multiselect("Track Type", options=df['track_type'].unique().tolist())
    if track_types:
        df_filtered = df_filtered[df_filtered['track_type'].isin(track_types)]
        
    # Map visual ranks to actual values for filtering
    rank_mapping = {'G1': 1, 'G2': 2, 'G3': 3, 'Local': 4, 'Non-Graded': 0}
    ranks = st.sidebar.multiselect("Race Rank", options=list(rank_mapping.keys()))
    if ranks:
        rank_vals = [rank_mapping[r] for r in ranks]
        df_filtered = df_filtered[df_filtered['race_rank'].isin(rank_vals)]
        
    st.sidebar.markdown("---")
    st.sidebar.header("🎲 Generation Modes")

    diff_countries = st.sidebar.toggle("🌍 Different Countries", value=False, help="Force each generated race to come from a different country.")

    # Mode 2: Director Mode Generation
    if st.session_state.director_mode:
        st.sidebar.markdown("---")
        st.sidebar.header("🎬 Director Controls")
        
        # Director's Chaos Master Controls in Sidebar
        sc1, sc2 = st.sidebar.columns(2)
        if sc1.button("Force Firm", use_container_width=True):
            for s in st.session_state.director_slots: s['ground'] = 'Firm'
            st.rerun()
        if sc2.button("Force Fair", use_container_width=True):
            for s in st.session_state.director_slots: s['weather'] = 'Fair'
            st.rerun()
        if st.sidebar.button("Reset All Slots", use_container_width=True):
            st.session_state.director_slots = [{'race_name': None, 'rank': 'Auto', 'weather': 'Auto', 'ground': 'Auto', 'time': 'Auto'} for _ in range(5)]
            st.rerun()

        if st.sidebar.button("✨ GENERATE DIRECTOR PACK", use_container_width=True):
            st.session_state.gen_id += 1
            st.session_state.is_animating = True
            st.session_state.race_environments = {}
            
            pack = []
            anchor_country = None
            main_surface = None
            
            # Check for anchor and surface sync from manually allocated races
            for slot in st.session_state.director_slots:
                if slot['race_name']:
                    matches = df[df['race_name'] == slot['race_name']]
                    if not matches.empty:
                        r_ref = matches.iloc[0]
                        anchor_country = r_ref['country']
                        if 'Dirt' in r_ref['track_type']: main_surface = 'Dirt'
            
            for i in range(5):
                slot = st.session_state.director_slots[i]
                if slot['race_name']:
                    # Allocated
                    pack.append(df[df['race_name'] == slot['race_name']].iloc[0].to_dict())
                else:
                    # Smart Filler
                    pool = df_filtered.copy()
                    
                    # Prestige Ladder Logic
                    s5 = st.session_state.director_slots[4]
                    is_s5_g1 = s5['rank'] == 'G1' or (s5['race_name'] and str(df[df['race_name'] == s5['race_name']].iloc[0]['race_rank']) == '1')
                    
                    target_rank = slot['rank']
                    if target_rank == 'Auto':
                        if is_s5_g1:
                            if i < 2: target_rank = 'Prelude'
                            elif i < 4: target_rank = 'Qualifier'
                            else: target_rank = 'G1'
                    
                    r_map = {'G1': [1], 'G2': [2], 'G3': [3], 'Local': [4], 'Non-Graded': [0], 'Prelude': [4, 0], 'Qualifier': [2, 3]}
                    
                    # Geographic Anchor Stickiness (Tiered Search)
                    final_choice = None
                    
                    # Tier 1: Sidebar Filters + Rank + Surface + Anchor
                    t1_pool = pool.copy()
                    if target_rank != 'Auto':
                        r_vals = r_map.get(target_rank, [1,2,3,4,0])
                        t1_pool = t1_pool[t1_pool['race_rank'].isin(r_vals)]
                        
                    if main_surface == 'Dirt':
                        t1_pool = t1_pool[t1_pool['track_type'].str.contains('Dirt', case=False, na=False)]
                    elif main_surface:
                        t1_pool = t1_pool[~t1_pool['track_type'].str.contains('Dirt', case=False, na=False)]
                    
                    if anchor_country:
                        country_pool = t1_pool[t1_pool['country'] == anchor_country]
                        if not country_pool.empty: t1_pool = country_pool
                    
                    if not t1_pool.empty:
                        final_choice = t1_pool.sample(1).iloc[0].to_dict()
                    
                    # Tier 2: Anchor + Rank (Ignore sidebar filters)
                    if not final_choice and anchor_country:
                        t2_pool = df.copy()
                        if target_rank != 'Auto':
                            r_vals = r_map.get(target_rank, [1,2,3,4,0])
                            t2_pool = t2_pool[t2_pool['race_rank'].isin(r_vals)]
                        
                        country_pool = t2_pool[t2_pool['country'] == anchor_country]
                        if country_pool.empty:
                            ref_row = df[df['country'] == anchor_country]
                            if not ref_row.empty:
                                continent = ref_row.iloc[0].get('continent')
                                if continent: t2_pool = t2_pool[t2_pool['continent'] == continent]
                        else:
                            t2_pool = country_pool
                            
                        if not t2_pool.empty:
                            final_choice = t2_pool.sample(1).iloc[0].to_dict()

                    # Tier 3: Global Rank Fallback
                    if not final_choice:
                        t3_pool = df.copy()
                        if target_rank != 'Auto':
                            r_vals = r_map.get(target_rank, [1,2,3,4,0])
                            t3_pool = t3_pool[t3_pool['race_rank'].isin(r_vals)]
                        if not t3_pool.empty:
                            final_choice = t3_pool.sample(1).iloc[0].to_dict()
                        else:
                            final_choice = df.sample(1).iloc[0].to_dict()
                            
                    pack.append(final_choice)
            
            st.session_state.generated_races = pd.DataFrame(pack)
            for i, row in st.session_state.generated_races.iterrows():
                slot = st.session_state.director_slots[i]
                lat = float(row.get('latitude', 0) or 0)
                season = get_season_for_hemisphere(current_month, lat)
                env = simulate_race_environment(lat, season, time_of_day)
                # Overrides
                if slot['weather'] != 'Auto': env['weather'] = slot['weather']
                if slot['ground'] != 'Auto': env['ground'] = slot['ground']
                if slot['time'] != 'Auto': env['time_of_day'] = slot['time']
                env['season'] = season
                st.session_state.race_environments[i] = env


    if st.sidebar.button("Generate Uma 5-Race Pack", use_container_width=True):
        st.session_state.gen_id += 1
        st.session_state.is_animating = True
        st.session_state.race_environments = {}
        pack = []

        if diff_countries:
            # --- Country-diverse mode ---
            # Build 5 candidate pools (by surface/distance), then pick from distinct countries
            pools = [
                df_filtered[df_filtered['track_type'].str.contains('Turf|Synthetic', case=False, na=False) & (df_filtered['length_type'] == 'Sprint')],
                df_filtered[df_filtered['track_type'].str.contains('Turf|Synthetic', case=False, na=False) & (df_filtered['length_type'] == 'Mile')],
                df_filtered[df_filtered['track_type'].str.contains('Turf|Synthetic', case=False, na=False) & (df_filtered['length_type'] == 'Medium')],
                df_filtered[df_filtered['track_type'].str.contains('Turf|Synthetic', case=False, na=False) & (df_filtered['length_type'] == 'Long')],
                df_filtered[df_filtered['track_type'].str.contains('Dirt', case=False, na=False)],
            ]
            used_countries = set()
            random.shuffle(pools)  # randomise which pool gets first country pick
            for pool in pools:
                if pool.empty:
                    continue
                # Prefer countries not yet used
                available = pool[~pool['country'].isin(used_countries)]
                if available.empty:
                    available = pool  # fall back to any country if exhausted
                chosen = available.sample(1)
                pack.append(chosen)
                used_countries.add(chosen.iloc[0]['country'])
        else:
            # --- Standard mode ---
            cond1 = df_filtered['track_type'].str.contains('Turf|Synthetic', case=False, na=False) & (df_filtered['length_type'] == 'Sprint')
            pool1 = df_filtered[cond1]
            if not pool1.empty: pack.append(pool1.sample(1))

            cond2 = df_filtered['track_type'].str.contains('Turf|Synthetic', case=False, na=False) & (df_filtered['length_type'] == 'Mile')
            pool2 = df_filtered[cond2]
            if not pool2.empty: pack.append(pool2.sample(1))

            cond3 = df_filtered['track_type'].str.contains('Turf|Synthetic', case=False, na=False) & (df_filtered['length_type'] == 'Medium')
            pool3 = df_filtered[cond3]
            if not pool3.empty: pack.append(pool3.sample(1))

            cond4 = df_filtered['track_type'].str.contains('Turf|Synthetic', case=False, na=False) & (df_filtered['length_type'] == 'Long')
            pool4 = df_filtered[cond4]
            if not pool4.empty: pack.append(pool4.sample(1))

            cond5 = df_filtered['track_type'].str.contains('Dirt', case=False, na=False)
            pool5 = df_filtered[cond5]
            if not pool5.empty: pack.append(pool5.sample(1))

        if len(pack) > 0:
            random.shuffle(pack)

        if len(pack) == 5:
            st.session_state.generated_races = pd.concat(pack).reset_index(drop=True)
        else:
            st.error(f"Could not generate full standard pack with current filters. Only found {len(pack)}/5 required race types.")
            if len(pack) > 0:
                st.session_state.generated_races = pd.concat(pack).reset_index(drop=True)
            else:
                st.session_state.generated_races = pd.DataFrame()

    # --- Mode 2b: AceStudio 5-Race Pack ---
    if st.sidebar.button("Generate AceStudio 5-Race Pack", use_container_width=True):
        st.session_state.gen_id += 1
        st.session_state.is_animating = True
        st.session_state.race_environments = {}
        pack = []

        if diff_countries:
            # --- Country-diverse AceStudio mode ---
            # 1st: Turf/Synthetic Medium
            pool_1 = df_filtered[df_filtered['track_type'].str.contains('Turf|Synthetic', case=False, na=False) & (df_filtered['length_type'] == 'Medium')]
            used_countries = set()
            if not pool_1.empty:
                race_1 = pool_1.sample(1)
                pack.append(race_1)
                used_countries.add(race_1.iloc[0]['country'])
                first_race_length = race_1.iloc[0]['length']
            
            # 2nd: Turf/Synthetic Sprint
            pool_2 = df_filtered[df_filtered['track_type'].str.contains('Turf|Synthetic', case=False, na=False) & (df_filtered['length_type'] == 'Sprint')]
            if not pool_2.empty:
                available = pool_2[~pool_2['country'].isin(used_countries)]
                if available.empty: available = pool_2
                race_2 = available.sample(1)
                pack.append(race_2)
                used_countries.add(race_2.iloc[0]['country'])
            
            # 3rd: Turf/Synthetic Medium, longer than 1st race
            if len(pack) >= 1:
                pool_3 = df_filtered[
                    df_filtered['track_type'].str.contains('Turf|Synthetic', case=False, na=False) & 
                    (df_filtered['length_type'] == 'Medium') &
                    (df_filtered['length'] > first_race_length)
                ]
                if not pool_3.empty:
                    available = pool_3[~pool_3['country'].isin(used_countries)]
                    if available.empty: available = pool_3
                    race_3 = available.sample(1)
                    pack.append(race_3)
                    used_countries.add(race_3.iloc[0]['country'])
            
            # 4th: Turf/Synthetic Mile
            pool_4 = df_filtered[df_filtered['track_type'].str.contains('Turf|Synthetic', case=False, na=False) & (df_filtered['length_type'] == 'Mile')]
            if not pool_4.empty:
                available = pool_4[~pool_4['country'].isin(used_countries)]
                if available.empty: available = pool_4
                race_4 = available.sample(1)
                pack.append(race_4)
                used_countries.add(race_4.iloc[0]['country'])
            
            # 5th: Turf/Synthetic Long
            pool_5 = df_filtered[df_filtered['track_type'].str.contains('Turf|Synthetic', case=False, na=False) & (df_filtered['length_type'] == 'Long')]
            if not pool_5.empty:
                available = pool_5[~pool_5['country'].isin(used_countries)]
                if available.empty: available = pool_5
                race_5 = available.sample(1)
                pack.append(race_5)
                used_countries.add(race_5.iloc[0]['country'])
        else:
            # --- Standard AceStudio mode ---
            # 1st: Turf/Synthetic Medium
            pool_1 = df_filtered[df_filtered['track_type'].str.contains('Turf|Synthetic', case=False, na=False) & (df_filtered['length_type'] == 'Medium')]
            if not pool_1.empty:
                race_1 = pool_1.sample(1)
                pack.append(race_1)
                first_race_length = race_1.iloc[0]['length']
            
            # 2nd: Turf/Synthetic Sprint
            pool_2 = df_filtered[df_filtered['track_type'].str.contains('Turf|Synthetic', case=False, na=False) & (df_filtered['length_type'] == 'Sprint')]
            if not pool_2.empty:
                pack.append(pool_2.sample(1))
            
            # 3rd: Turf/Synthetic Medium, longer than 1st race
            if len(pack) >= 1:
                pool_3 = df_filtered[
                    df_filtered['track_type'].str.contains('Turf|Synthetic', case=False, na=False) & 
                    (df_filtered['length_type'] == 'Medium') &
                    (df_filtered['length'] > first_race_length)
                ]
                if not pool_3.empty:
                    pack.append(pool_3.sample(1))
            
            # 4th: Turf/Synthetic Mile
            pool_4 = df_filtered[df_filtered['track_type'].str.contains('Turf|Synthetic', case=False, na=False) & (df_filtered['length_type'] == 'Mile')]
            if not pool_4.empty:
                pack.append(pool_4.sample(1))
            
            # 5th: Turf/Synthetic Long
            pool_5 = df_filtered[df_filtered['track_type'].str.contains('Turf|Synthetic', case=False, na=False) & (df_filtered['length_type'] == 'Long')]
            if not pool_5.empty:
                pack.append(pool_5.sample(1))
        
        if len(pack) == 5:
            st.session_state.generated_races = pd.concat(pack).reset_index(drop=True)
        else:
            st.error(f"Could not generate full AceStudio pack with current filters. Only found {len(pack)}/5 required race types.")
            if len(pack) > 0:
                st.session_state.generated_races = pd.concat(pack).reset_index(drop=True)
            else:
                st.session_state.generated_races = pd.DataFrame()

    # --- Mode 3: Custom N-Race Pack ---
    num_custom = st.sidebar.slider("Number of Races", 1, 30, 10)
    if st.sidebar.button(f"✨ GENERATE CUSTOM {num_custom}-RACE PACK", use_container_width=True):
        st.session_state.gen_id += 1
        st.session_state.is_animating = True
        st.session_state.race_environments = {}
        # Custom generation respecting diff_countries
        if diff_countries:
            unique_countries = df_filtered['country'].unique().tolist()
            random.shuffle(unique_countries)
            pack = []
            
            # Keep track of indices to avoid duplicates if possible
            available_df = df_filtered.copy()
            
            while len(pack) < num_custom and not available_df.empty:
                for country in unique_countries:
                    if len(pack) >= num_custom: break
                    
                    country_pool = available_df[available_df['country'] == country]
                    if not country_pool.empty:
                        chosen = country_pool.sample(1)
                        pack.append(chosen)
                        # Remove chosen race from future picks to avoid duplicates
                        available_df = available_df.drop(chosen.index)
                
                # If we've cycled through all countries but still need more, 
                # they will naturally repeat in the next while-loop iteration 
                # (but with different races from those countries if available)
                if all(available_df[available_df['country'] == c].empty for c in unique_countries):
                    break
            
            if pack:
                st.session_state.generated_races = pd.concat(pack).reset_index(drop=True)
            else:
                st.session_state.generated_races = pd.DataFrame()
        else:
            st.session_state.generated_races = df_filtered.sample(min(num_custom, len(df_filtered))).reset_index(drop=True)

    st.sidebar.markdown("---")
    # Simulate environment for each race
    for i, row in st.session_state.generated_races.iterrows():
        lat = float(row.get('latitude', 0) or 0)
        season = get_season_for_hemisphere(current_month, lat)
        env = simulate_race_environment(lat, season, time_of_day)
        env['season'] = season
        env['time_of_day'] = time_of_day
        st.session_state.race_environments[i] = env

    # --- Main Content Area ---
    if st.session_state.director_mode:
        st.markdown("### 🎬 Race Director Timeline")
        slot_cols = st.columns(5)
        for i in range(5):
            slot = st.session_state.director_slots[i]
            is_filled = slot['race_name'] is not None
            is_manual = slot['rank'] != 'Auto' or slot['weather'] != 'Auto' or slot['ground'] != 'Auto' or slot['time'] != 'Auto'
            
            box_style = "slot-filled" if is_filled else ""
            manual_badge = '<div class="slot-manual-indicator">!</div>' if is_manual else ""
            with slot_cols[i]:
                if is_filled:
                    # Render Actual Card HTML
                    matches = df[(df['race_name'] == slot['race_name']) & (df['racetrack'] == slot['racetrack']) & (df['length'] == slot['length'])]
                    if not matches.empty:
                        st.markdown(render_card_html(matches.iloc[0]), unsafe_allow_html=True)
                        
                        if st.session_state.selected_stable_race:
                            if st.button("🔄 SWAP SLOT", key=f"swap_{i}", use_container_width=True):
                                # Displacement: send old race back to Stable
                                old_race = matches.iloc[0].to_dict()
                                active_l = list(st.session_state.user_groups.keys())[0] # Default fallback
                                st.session_state.user_groups[active_l].append(old_race)
                                save_user_groups(st.session_state.user_groups)
                                
                                # Insert new race
                                slot['race_name'] = st.session_state.selected_stable_race['race_name']
                                slot['racetrack'] = st.session_state.selected_stable_race['racetrack']
                                slot['length'] = st.session_state.selected_stable_race['length']
                                st.session_state.selected_stable_race = None
                                st.rerun()

                elif st.session_state.selected_stable_race:
                    # Drop Zone
                    if st.button(f"📥 PLACE HERE", key=f"drop_{i}", use_container_width=True):
                        slot['race_name'] = st.session_state.selected_stable_race['race_name']
                        slot['racetrack'] = st.session_state.selected_stable_race['racetrack']
                        slot['length'] = st.session_state.selected_stable_race['length']
                        st.session_state.selected_stable_race = None # Consume
                        st.rerun()
                
                label = "Slot Settings" if is_filled else f"Slot {i+1}\n(Auto)"
                if st.button(label, key=f"slot_btn_{i}", use_container_width=True):
                    st.session_state[f"edit_slot_{i}"] = not st.session_state.get(f"edit_slot_{i}", False)
                
                if st.session_state.get(f"edit_slot_{i}", False):
                    with st.expander(f"⚙️ Slot {i+1} Settings", expanded=True):
                        # Search
                        s_query = st.text_input("Find Race", key=f"search_{i}")
                        if s_query:
                            res = df[df['race_name'].str.contains(s_query, case=False, na=False)]
                            if not res.empty:
                                chosen = st.selectbox("Select", res['race_name'].tolist(), key=f"sel_{i}")
                                if st.button("Allocate", key=f"alloc_{i}"):
                                    slot['race_name'] = chosen
                                    st.rerun()
                        
                        if st.button("Clear Slot", key=f"clear_{i}", use_container_width=True):
                            st.session_state.director_slots[i] = {
                                'race_name': None, 'racetrack': None, 'length': None,
                                'rank': 'Auto', 'weather': 'Auto', 'ground': 'Auto', 'time': 'Auto'
                            }
                            # Explicitly reset widget keys to force UI update
                            st.session_state[f"r_{i}"] = 'Auto'
                            st.session_state[f"w_{i}"] = 'Auto'
                            st.session_state[f"g_{i}"] = 'Auto'
                            st.session_state[f"t_{i}"] = 'Auto'
                            st.rerun()

                        slot['rank'] = st.selectbox("Rank", ['Auto', 'G1', 'G2', 'G3', 'Local', 'Non-Graded'], index=['Auto', 'G1', 'G2', 'G3', 'Local', 'Non-Graded'].index(slot['rank']), key=f"r_{i}")
                        slot['weather'] = st.selectbox("Weather", ['Auto', 'Fair', 'Cloudy', 'Rainy', 'Snowy'], index=['Auto', 'Fair', 'Cloudy', 'Rainy', 'Snowy'].index(slot['weather']), key=f"w_{i}")
                        slot['ground'] = st.selectbox("Ground", ['Auto', 'Firm', 'Good', 'Soft', 'Heavy'], index=['Auto', 'Firm', 'Good', 'Soft', 'Heavy'].index(slot['ground']), key=f"g_{i}")
                        slot['time'] = st.selectbox("Time", ['Auto', 'Midday', 'Evening', 'Night'], index=['Auto', 'Midday', 'Evening', 'Night'].index(slot['time']), key=f"t_{i}")

    if not st.session_state.generated_races.empty:
        st.markdown(f'<h4 style="margin:0 0 5px 0; padding:0; font-size: 1.1em;">🏁 GENERATED RACES ({len(st.session_state.generated_races)})</h4>', unsafe_allow_html=True)
        # Dashboard Layout: 2 Columns
        main_col_left, main_col_right = st.columns([1, 1], gap="small")
        
        with main_col_left:
            num_races = len(st.session_state.generated_races)
            
            card_placeholders = []
            btn_placeholders = []
            
            for i in range(0, num_races, 2):
                row_cols = st.columns(2)
                with row_cols[0]:
                    card_placeholders.append(st.empty())
                    btn_placeholders.append(st.empty())
                if i + 1 < num_races:
                    with row_cols[1]:
                        card_placeholders.append(st.empty())
                        btn_placeholders.append(st.empty())
            
            def render_card_entry(card_p, btn_p, row, idx, is_selected, show_buttons=True):
                card_p.markdown(render_card_html(row, is_selected), unsafe_allow_html=True)
                if show_buttons:
                    with btn_p:
                        b_col1, b_col2 = st.columns([4, 1])
                        if b_col1.button("📍 Focus", key=f"race_btn_{st.session_state.gen_id}_{idx}", use_container_width=True):
                            st.session_state.selected_race_idx = idx
                            st.rerun()
                        if b_col2.button("➕", key=f"collect_{st.session_state.gen_id}_{idx}", help="Save to Stable", use_container_width=True):
                            active_l = list(st.session_state.user_groups.keys())[0] # Add to first lib by default
                            st.session_state.user_groups[active_l].append(row.to_dict())
                            save_user_groups(st.session_state.user_groups)
                            st.toast(f"Added {row['race_name']} to {active_l}")
                else:
                    btn_p.empty()
            
            # Render state
            is_animating = st.session_state.get('is_animating', False)
            
            if is_animating:
                for idx in range(num_races):
                    card_placeholders[idx].markdown(render_pending_card(), unsafe_allow_html=True)
                    btn_placeholders[idx].empty()
            else:
                for idx, row in st.session_state.generated_races.iterrows():
                    render_card_entry(card_placeholders[idx], btn_placeholders[idx], row, idx, st.session_state.selected_race_idx == idx)

        with main_col_right:
            map_placeholder = st.empty()
            detail_placeholder = st.empty()
            
            if st.session_state.get('is_animating', False):
                st.session_state.is_animating = False
                chime_b64 = get_base64_of_bin_file('bell_chime.wav')
                fanfare_b64 = get_base64_of_bin_file('fanfare.wav')
                highlighted = []
                
                # Render empty globe initially
                display_map_with_hud(map_placeholder, [], 0)
                
                for i, row in st.session_state.generated_races.iterrows():
                    # 0. RE-RENDER PREVIOUS CARDS
                    for prev_idx in range(i):
                        prev_row = st.session_state.generated_races.iloc[prev_idx]
                        card_placeholders[prev_idx].markdown(render_card_html(prev_row, False), unsafe_allow_html=True)
                        btn_placeholders[prev_idx].empty()

                    # 1. Flickering Effect
                    audio_played = False
                    for _ in range(10):
                        rand_row = df.sample(1).iloc[0]
                        card_placeholders[i].markdown(render_card_html(rand_row), unsafe_allow_html=True)
                        
                        if not audio_played and chime_b64:
                            st.markdown(f'<audio autoplay><source src="data:audio/wav;base64,{chime_b64}" type="audio/wav"></audio>', unsafe_allow_html=True)
                            audio_played = True
                        time.sleep(0.2)
                    
                    # 2. Final Reveal (No buttons during animation)
                    st.session_state.selected_race_idx = i
                    card_placeholders[i].markdown(render_card_html(row, True), unsafe_allow_html=True)
                    btn_placeholders[i].empty()
                    
                    highlighted.append(row.to_dict())
                    # Update globe to focus on the newly revealed race
                    display_map_with_hud(map_placeholder, highlighted, i)
                    with detail_placeholder:
                        env_i = st.session_state.race_environments.get(i, {})
                        render_full_detail_card(row, env_i)
                    time.sleep(0.8) # Brief pause after reveal before starting next card
                
                if fanfare_b64:
                    st.markdown(f'<audio autoplay><source src="data:audio/wav;base64,{fanfare_b64}" type="audio/wav"></audio>', unsafe_allow_html=True)
                    time.sleep(3.0)  # Wait for fanfare to finish before rerunning

                st.rerun()
            else:
                # Normal State Rendering for Globe/Detail
                highlighted = st.session_state.generated_races.to_dict('records')
                sel_idx = st.session_state.selected_race_idx
                
                display_map_with_hud(map_placeholder, highlighted, sel_idx)
                with detail_placeholder:
                    env = st.session_state.race_environments.get(sel_idx, {})
                    render_full_detail_card(st.session_state.generated_races.iloc[sel_idx], env)
                    
    else:
        if not st.session_state.director_mode:
            st.markdown('<div style="background-color: rgba(0,0,0,0.5); color: #ffffff; padding: 25px; border-radius: 12px; border-left: 5px solid #bf94ff; font-weight: bold; font-size: 1.2em;">👈 Use the sidebar to generate your race pack and start the sequence.</div>', unsafe_allow_html=True)
                

if __name__ == "__main__":
    main()
