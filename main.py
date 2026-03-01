"""
SkillBond - Android APK
Built with Kivy 2.3.0 + KivyMD 2.0.1 + Python 3.10.11
Dark modern theme | Multi-user | Local SQLite | Live autocomplete

Fixes in this version:
  - REMOVED icon_left from ALL MDTextFields (was causing crash on Android)
  - Quick skill chips now wrap into rows properly (no overlap/cutoff)
  - Auto-login: session saved by user_id so user stays logged in
  - Call button on friend cards opens phone dialer with number pre-filled
"""

import os
import json

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window

from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.widget import MDWidget

try:
    from kivymd.uix.dialog import (
        MDDialogHeadlineText,
        MDDialogSupportingText,
        MDDialogButtonContainer,
    )
    DIALOG_V2 = True
except ImportError:
    DIALOG_V2 = False

from db import Database

# ── Palette ───────────────────────────────────────────────────────────────────
C_BG       = "#080b12"
C_CARD     = "#0e1220"
C_ELEVATED = "#151c2c"
C_ACCENT   = "#00d4ff"
C_ACCENT2  = "#7c3aed"
C_TEXT     = "#f0f4ff"
C_SECOND   = "#8892a4"
C_MUTED    = "#4a5568"
C_DANGER   = "#ef4444"
C_BORDER   = "#1a2035"

AVATAR_COLORS = [
    "#00d4ff", "#7c3aed", "#10b981", "#f59e0b",
    "#ef4444", "#3b82f6", "#ec4899", "#06b6d4",
]

QUICK_SKILLS = [
    "Python", "JavaScript", "Design", "Photography",
    "Video Editing", "Driving", "Cooking", "English",
    "Accounting", "Teaching", "Medical", "Plumbing",
]

# ── KV ────────────────────────────────────────────────────────────────────────
KV = """
#:import dp kivy.metrics.dp
#:import hex kivy.utils.get_color_from_hex

<SkillBondSM>:
    LoginScreen:
        name: 'login'
    RegisterScreen:
        name: 'register'
    DashboardScreen:
        name: 'dashboard'
    AddEditScreen:
        name: 'add_edit'

# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN SCREEN
# ══════════════════════════════════════════════════════════════════════════════
<LoginScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: hex("#080b12")
        padding: [dp(28), dp(0)]

        MDWidget:
            size_hint_y: None
            height: dp(56)

        MDCard:
            orientation: 'vertical'
            padding: dp(28)
            spacing: dp(10)
            size_hint: 1, None
            height: dp(180)
            md_bg_color: hex("#0e1220")
            line_color: hex("#1a2035")
            radius: [dp(20)]
            elevation: 0

            MDIcon:
                icon: 'account-group'
                halign: 'center'
                theme_text_color: 'Custom'
                text_color: hex("#00d4ff")
                font_size: dp(44)
                size_hint_y: None
                height: dp(52)

            MDLabel:
                text: 'SkillBond'
                halign: 'center'
                theme_text_color: 'Custom'
                text_color: hex("#f0f4ff")
                font_size: '24sp'
                bold: True
                size_hint_y: None
                height: dp(36)

            MDLabel:
                text: 'Find the Right Friend, Fast'
                halign: 'center'
                theme_text_color: 'Custom'
                text_color: hex("#8892a4")
                font_size: '12sp'
                size_hint_y: None
                height: dp(20)

        MDWidget:
            size_hint_y: None
            height: dp(18)

        MDCard:
            orientation: 'vertical'
            padding: [dp(24), dp(20)]
            spacing: dp(8)
            size_hint: 1, None
            height: dp(290)
            md_bg_color: hex("#0e1220")
            line_color: hex("#1a2035")
            radius: [dp(20)]
            elevation: 0

            MDLabel:
                text: "Username"
                theme_text_color: "Custom"
                text_color: hex("#8892a4")
                font_size: "12sp"
                size_hint_y: None
                height: dp(18)

            MDTextField:
                id: login_username
                hint_text: "Enter your username"
                mode: "outlined"
                theme_text_color: "Custom"
                text_color_normal: hex("#f0f4ff")
                text_color_focus: hex("#f0f4ff")
                hint_text_color_normal: hex("#8892a4")
                hint_text_color_focus: hex("#8892a4")
                line_color_normal: hex("#2a3a55")
                line_color_focus: hex("#00d4ff")
                size_hint_y: None
                height: dp(52)

            MDLabel:
                text: "Password"
                theme_text_color: "Custom"
                text_color: hex("#8892a4")
                font_size: "12sp"
                size_hint_y: None
                height: dp(18)

            MDTextField:
                id: login_password
                hint_text: "Enter your password"
                mode: "outlined"
                password: True
                theme_text_color: "Custom"
                text_color_normal: hex("#f0f4ff")
                text_color_focus: hex("#f0f4ff")
                hint_text_color_normal: hex("#8892a4")
                hint_text_color_focus: hex("#8892a4")
                line_color_normal: hex("#2a3a55")
                line_color_focus: hex("#00d4ff")
                size_hint_y: None
                height: dp(52)

            MDButton:
                style: "filled"
                size_hint_x: 1
                on_release: root.do_login()
                theme_bg_color: "Custom"
                md_bg_color: hex("#00d4ff")
                MDButtonText:
                    text: "LOGIN"
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 1
                    bold: True

        MDWidget:
            size_hint_y: None
            height: dp(16)

        MDLabel:
            text: "Don't have an account?  [color=#00d4ff][ref=go]Sign Up[/ref][/color]"
            halign: 'center'
            markup: True
            theme_text_color: 'Custom'
            text_color: hex("#8892a4")
            size_hint_y: None
            height: dp(38)
            on_ref_press: app.root.current = 'register'

        MDWidget:

# ══════════════════════════════════════════════════════════════════════════════
#  REGISTER SCREEN
# ══════════════════════════════════════════════════════════════════════════════
<RegisterScreen>:
    MDScrollView:
        MDBoxLayout:
            orientation: 'vertical'
            md_bg_color: hex("#080b12")
            padding: [dp(28), dp(20)]
            spacing: dp(14)
            adaptive_height: True

            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(44)
                spacing: dp(6)

                MDIconButton:
                    icon: 'arrow-left'
                    theme_icon_color: "Custom"
                    icon_color: hex("#00d4ff")
                    on_release: app.root.current = 'login'

                MDLabel:
                    text: 'Create Account'
                    theme_text_color: 'Custom'
                    text_color: hex("#f0f4ff")
                    font_size: '20sp'
                    bold: True
                    valign: 'center'

            MDCard:
                orientation: 'vertical'
                padding: [dp(24), dp(20)]
                spacing: dp(8)
                size_hint: 1, None
                height: dp(420)
                md_bg_color: hex("#0e1220")
                line_color: hex("#1a2035")
                radius: [dp(20)]
                elevation: 0

                MDLabel:
                    text: "Username (min 3 characters)"
                    theme_text_color: "Custom"
                    text_color: hex("#8892a4")
                    font_size: "12sp"
                    size_hint_y: None
                    height: dp(18)

                MDTextField:
                    id: reg_username
                    hint_text: "Choose a username"
                    mode: "outlined"
                    theme_text_color: "Custom"
                    text_color_normal: hex("#f0f4ff")
                    text_color_focus: hex("#f0f4ff")
                    hint_text_color_normal: hex("#8892a4")
                    hint_text_color_focus: hex("#8892a4")
                    line_color_normal: hex("#2a3a55")
                    line_color_focus: hex("#7c3aed")
                    size_hint_y: None
                    height: dp(52)

                MDLabel:
                    text: "Password (min 6 characters)"
                    theme_text_color: "Custom"
                    text_color: hex("#8892a4")
                    font_size: "12sp"
                    size_hint_y: None
                    height: dp(18)

                MDTextField:
                    id: reg_password
                    hint_text: "Choose a password"
                    mode: "outlined"
                    password: True
                    theme_text_color: "Custom"
                    text_color_normal: hex("#f0f4ff")
                    text_color_focus: hex("#f0f4ff")
                    hint_text_color_normal: hex("#8892a4")
                    hint_text_color_focus: hex("#8892a4")
                    line_color_normal: hex("#2a3a55")
                    line_color_focus: hex("#7c3aed")
                    size_hint_y: None
                    height: dp(52)

                MDLabel:
                    text: "Confirm Password"
                    theme_text_color: "Custom"
                    text_color: hex("#8892a4")
                    font_size: "12sp"
                    size_hint_y: None
                    height: dp(18)

                MDTextField:
                    id: reg_confirm
                    hint_text: "Re-enter your password"
                    mode: "outlined"
                    password: True
                    theme_text_color: "Custom"
                    text_color_normal: hex("#f0f4ff")
                    text_color_focus: hex("#f0f4ff")
                    hint_text_color_normal: hex("#8892a4")
                    hint_text_color_focus: hex("#8892a4")
                    line_color_normal: hex("#2a3a55")
                    line_color_focus: hex("#7c3aed")
                    size_hint_y: None
                    height: dp(52)

                MDButton:
                    style: "filled"
                    size_hint_x: 1
                    on_release: root.do_register()
                    theme_bg_color: "Custom"
                    md_bg_color: hex("#7c3aed")
                    MDButtonText:
                        text: "CREATE ACCOUNT"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        bold: True

            MDLabel:
                text: "Have an account?  [color=#00d4ff][ref=go]Login[/ref][/color]"
                halign: 'center'
                markup: True
                theme_text_color: 'Custom'
                text_color: hex("#8892a4")
                size_hint_y: None
                height: dp(38)
                on_ref_press: app.root.current = 'login'

# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD SCREEN
# ══════════════════════════════════════════════════════════════════════════════
<DashboardScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: hex("#080b12")

        MDBoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(56)
            padding: [dp(14), dp(8)]
            spacing: dp(8)
            md_bg_color: hex("#0e1220")

            MDIcon:
                icon: 'account-group'
                theme_text_color: 'Custom'
                text_color: hex("#00d4ff")
                size_hint_x: None
                width: dp(28)

            MDLabel:
                text: 'SkillBond'
                theme_text_color: 'Custom'
                text_color: hex("#f0f4ff")
                font_size: '20sp'
                bold: True

            MDLabel:
                id: topbar_user
                text: ''
                halign: 'right'
                theme_text_color: 'Custom'
                text_color: hex("#8892a4")
                font_size: '12sp'

            MDIconButton:
                icon: 'logout'
                theme_icon_color: "Custom"
                icon_color: hex("#8892a4")
                size_hint_x: None
                width: dp(40)
                on_release: root.do_logout()

        MDScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                padding: [dp(14), dp(12)]
                spacing: dp(12)
                adaptive_height: True

                # Stats row
                MDBoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: dp(88)
                    spacing: dp(8)

                    MDCard:
                        orientation: 'vertical'
                        padding: dp(10)
                        spacing: dp(4)
                        md_bg_color: hex("#0e1220")
                        line_color: hex("#1a2035")
                        radius: [dp(14)]
                        elevation: 0
                        MDLabel:
                            id: stat_friends_num
                            text: '0'
                            halign: 'center'
                            theme_text_color: 'Custom'
                            text_color: hex("#00d4ff")
                            font_size: '24sp'
                            bold: True
                            size_hint_y: None
                            height: dp(36)
                        MDLabel:
                            text: 'Friends'
                            halign: 'center'
                            theme_text_color: 'Custom'
                            text_color: hex("#8892a4")
                            font_size: '12sp'
                            size_hint_y: None
                            height: dp(20)

                    MDCard:
                        orientation: 'vertical'
                        padding: dp(10)
                        spacing: dp(4)
                        md_bg_color: hex("#0e1220")
                        line_color: hex("#1a2035")
                        radius: [dp(14)]
                        elevation: 0
                        MDLabel:
                            id: stat_skills_num
                            text: '0'
                            halign: 'center'
                            theme_text_color: 'Custom'
                            text_color: hex("#a78bfa")
                            font_size: '24sp'
                            bold: True
                            size_hint_y: None
                            height: dp(36)
                        MDLabel:
                            text: 'Skills'
                            halign: 'center'
                            theme_text_color: 'Custom'
                            text_color: hex("#8892a4")
                            font_size: '12sp'
                            size_hint_y: None
                            height: dp(20)

                    MDCard:
                        orientation: 'vertical'
                        padding: dp(10)
                        spacing: dp(4)
                        md_bg_color: hex("#0e1220")
                        line_color: hex("#1a2035")
                        radius: [dp(14)]
                        elevation: 0
                        MDLabel:
                            id: stat_locs_num
                            text: '0'
                            halign: 'center'
                            theme_text_color: 'Custom'
                            text_color: hex("#fbbf24")
                            font_size: '24sp'
                            bold: True
                            size_hint_y: None
                            height: dp(36)
                        MDLabel:
                            text: 'Locations'
                            halign: 'center'
                            theme_text_color: 'Custom'
                            text_color: hex("#8892a4")
                            font_size: '12sp'
                            size_hint_y: None
                            height: dp(20)

                # Search card
                MDCard:
                    orientation: 'vertical'
                    padding: [dp(14), dp(12)]
                    spacing: dp(6)
                    size_hint_y: None
                    height: self.minimum_height
                    md_bg_color: hex("#0e1220")
                    line_color: hex("#1a2035")
                    radius: [dp(16)]
                    elevation: 0

                    MDLabel:
                        text: 'Search Friends'
                        theme_text_color: 'Custom'
                        text_color: hex("#f0f4ff")
                        font_size: '16sp'
                        bold: True
                        size_hint_y: None
                        height: dp(28)

                    MDLabel:
                        text: "Name"
                        theme_text_color: "Custom"
                        text_color: hex("#8892a4")
                        font_size: "11sp"
                        size_hint_y: None
                        height: dp(16)

                    MDTextField:
                        id: search_name
                        hint_text: "Search by name..."
                        mode: "outlined"
                        theme_text_color: "Custom"
                        text_color_normal: hex("#f0f4ff")
                        text_color_focus: hex("#f0f4ff")
                        hint_text_color_normal: hex("#8892a4")
                        hint_text_color_focus: hex("#8892a4")
                        line_color_normal: hex("#2a3a55")
                        line_color_focus: hex("#00d4ff")
                        size_hint_y: None
                        height: dp(50)

                    MDLabel:
                        text: "Skill"
                        theme_text_color: "Custom"
                        text_color: hex("#8892a4")
                        font_size: "11sp"
                        size_hint_y: None
                        height: dp(16)

                    MDTextField:
                        id: search_skill
                        hint_text: "Filter by skill..."
                        mode: "outlined"
                        theme_text_color: "Custom"
                        text_color_normal: hex("#f0f4ff")
                        text_color_focus: hex("#f0f4ff")
                        hint_text_color_normal: hex("#8892a4")
                        hint_text_color_focus: hex("#8892a4")
                        line_color_normal: hex("#2a3a55")
                        line_color_focus: hex("#00d4ff")
                        size_hint_y: None
                        height: dp(50)

                    MDBoxLayout:
                        id: skill_suggestions
                        orientation: 'vertical'
                        size_hint_y: None
                        adaptive_height: True
                        spacing: dp(2)

                    MDLabel:
                        text: "Location"
                        theme_text_color: "Custom"
                        text_color: hex("#8892a4")
                        font_size: "11sp"
                        size_hint_y: None
                        height: dp(16)

                    MDTextField:
                        id: search_location
                        hint_text: "Filter by location..."
                        mode: "outlined"
                        theme_text_color: "Custom"
                        text_color_normal: hex("#f0f4ff")
                        text_color_focus: hex("#f0f4ff")
                        hint_text_color_normal: hex("#8892a4")
                        hint_text_color_focus: hex("#8892a4")
                        line_color_normal: hex("#2a3a55")
                        line_color_focus: hex("#00d4ff")
                        size_hint_y: None
                        height: dp(50)

                    MDBoxLayout:
                        id: location_suggestions
                        orientation: 'vertical'
                        size_hint_y: None
                        adaptive_height: True
                        spacing: dp(2)

                # Results header
                MDBoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: dp(38)
                    spacing: dp(8)

                    MDLabel:
                        id: results_label
                        text: 'My Friends'
                        theme_text_color: 'Custom'
                        text_color: hex("#f0f4ff")
                        font_size: '16sp'
                        bold: True

                    MDWidget:

                    MDButton:
                        style: "filled"
                        size_hint_x: None
                        width: dp(88)
                        on_release: root.go_add_friend()
                        theme_bg_color: "Custom"
                        md_bg_color: hex("#00d4ff")
                        MDButtonText:
                            text: "+ ADD"
                            theme_text_color: "Custom"
                            text_color: 0, 0, 0, 1
                            bold: True

                MDBoxLayout:
                    id: friends_list
                    orientation: 'vertical'
                    spacing: dp(10)
                    adaptive_height: True

# ══════════════════════════════════════════════════════════════════════════════
#  ADD / EDIT FRIEND SCREEN
# ══════════════════════════════════════════════════════════════════════════════
<AddEditScreen>:
    MDScrollView:
        MDBoxLayout:
            orientation: 'vertical'
            md_bg_color: hex("#080b12")
            padding: [dp(18), dp(16)]
            spacing: dp(14)
            adaptive_height: True

            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(44)
                spacing: dp(6)

                MDIconButton:
                    icon: 'arrow-left'
                    theme_icon_color: "Custom"
                    icon_color: hex("#00d4ff")
                    on_release: root.go_back()

                MDLabel:
                    id: form_title
                    text: 'Add Friend'
                    theme_text_color: 'Custom'
                    text_color: hex("#f0f4ff")
                    font_size: '20sp'
                    bold: True
                    valign: 'center'

            # Form card — adaptive height, no overflow
            MDCard:
                orientation: 'vertical'
                padding: [dp(20), dp(16)]
                spacing: dp(6)
                size_hint_y: None
                height: self.minimum_height
                md_bg_color: hex("#0e1220")
                line_color: hex("#1a2035")
                radius: [dp(16)]
                elevation: 0

                MDLabel:
                    text: "Full Name *"
                    theme_text_color: "Custom"
                    text_color: hex("#8892a4")
                    font_size: "12sp"
                    size_hint_y: None
                    height: dp(18)

                MDTextField:
                    id: f_name
                    hint_text: "Enter full name"
                    mode: "outlined"
                    theme_text_color: "Custom"
                    text_color_normal: hex("#f0f4ff")
                    text_color_focus: hex("#f0f4ff")
                    hint_text_color_normal: hex("#8892a4")
                    hint_text_color_focus: hex("#8892a4")
                    line_color_normal: hex("#2a3a55")
                    line_color_focus: hex("#00d4ff")
                    size_hint_y: None
                    height: dp(52)

                MDLabel:
                    text: "Phone Number"
                    theme_text_color: "Custom"
                    text_color: hex("#8892a4")
                    font_size: "12sp"
                    size_hint_y: None
                    height: dp(18)

                MDTextField:
                    id: f_phone
                    hint_text: "e.g. +880 1234 567890"
                    mode: "outlined"
                    input_type: 'tel'
                    theme_text_color: "Custom"
                    text_color_normal: hex("#f0f4ff")
                    text_color_focus: hex("#f0f4ff")
                    hint_text_color_normal: hex("#8892a4")
                    hint_text_color_focus: hex("#8892a4")
                    line_color_normal: hex("#2a3a55")
                    line_color_focus: hex("#00d4ff")
                    size_hint_y: None
                    height: dp(52)

                MDLabel:
                    text: "Location / City"
                    theme_text_color: "Custom"
                    text_color: hex("#8892a4")
                    font_size: "12sp"
                    size_hint_y: None
                    height: dp(18)

                MDTextField:
                    id: f_location
                    hint_text: "e.g. Dhaka, Chittagong"
                    mode: "outlined"
                    theme_text_color: "Custom"
                    text_color_normal: hex("#f0f4ff")
                    text_color_focus: hex("#f0f4ff")
                    hint_text_color_normal: hex("#8892a4")
                    hint_text_color_focus: hex("#8892a4")
                    line_color_normal: hex("#2a3a55")
                    line_color_focus: hex("#00d4ff")
                    size_hint_y: None
                    height: dp(52)

                MDLabel:
                    text: "Skills (comma separated)"
                    theme_text_color: "Custom"
                    text_color: hex("#8892a4")
                    font_size: "12sp"
                    size_hint_y: None
                    height: dp(18)

                MDTextField:
                    id: f_skills
                    hint_text: "e.g. Python, Design, Cooking"
                    mode: "outlined"
                    theme_text_color: "Custom"
                    text_color_normal: hex("#f0f4ff")
                    text_color_focus: hex("#f0f4ff")
                    hint_text_color_normal: hex("#8892a4")
                    hint_text_color_focus: hex("#8892a4")
                    line_color_normal: hex("#2a3a55")
                    line_color_focus: hex("#00d4ff")
                    size_hint_y: None
                    height: dp(52)

                MDLabel:
                    text: "Notes (optional)"
                    theme_text_color: "Custom"
                    text_color: hex("#8892a4")
                    font_size: "12sp"
                    size_hint_y: None
                    height: dp(18)

                MDTextField:
                    id: f_notes
                    hint_text: "Any extra info about this person"
                    mode: "outlined"
                    multiline: True
                    theme_text_color: "Custom"
                    text_color_normal: hex("#f0f4ff")
                    text_color_focus: hex("#f0f4ff")
                    hint_text_color_normal: hex("#8892a4")
                    hint_text_color_focus: hex("#8892a4")
                    line_color_normal: hex("#2a3a55")
                    line_color_focus: hex("#00d4ff")
                    size_hint_y: None
                    height: dp(72)

            MDLabel:
                text: 'Quick Add Skills:'
                theme_text_color: 'Custom'
                text_color: hex("#8892a4")
                font_size: '13sp'
                bold: True
                size_hint_y: None
                height: dp(24)

            # Chip rows injected from Python
            MDBoxLayout:
                id: chips_container
                orientation: 'vertical'
                spacing: dp(8)
                size_hint_y: None
                adaptive_height: True

            MDButton:
                id: save_btn
                style: "filled"
                size_hint_x: 1
                on_release: root.do_save()
                theme_bg_color: "Custom"
                md_bg_color: hex("#00d4ff")
                MDButtonText:
                    id: save_btn_text
                    text: "SAVE FRIEND"
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 1
                    bold: True

            MDWidget:
                size_hint_y: None
                height: dp(20)
"""

Builder.load_string(KV)


# ══════════════════════════════════════════════════════════════════════════════
#  SCREEN MANAGER
# ══════════════════════════════════════════════════════════════════════════════
class SkillBondSM(ScreenManager):
    pass


# ══════════════════════════════════════════════════════════════════════════════
#  AUTOCOMPLETE  — inline suggestion list (no MDDropdownMenu, crash-safe)
# ══════════════════════════════════════════════════════════════════════════════
class Autocomplete:
    """
    Shows matching suggestions as tappable MDLabel rows in a container
    widget placed directly in the layout (below the field).
    No MDDropdownMenu — avoids the Android crash entirely.

    Usage:
        ac = Autocomplete(field, suggestion_box, get_items_fn, on_select_fn)
        # suggestion_box: an MDBoxLayout with adaptive_height=True placed
        #                 directly below the field in your layout.
    """

    def __init__(self, field: MDTextField, suggestion_box: MDBoxLayout,
                 get_items_fn, on_select_fn=None):
        self.field          = field
        self.box            = suggestion_box
        self.get_items      = get_items_fn
        self.on_select      = on_select_fn
        self._debounce      = None
        self._selecting     = False

        field.bind(text=self._on_text)
        field.bind(focus=self._on_focus)

    def _on_text(self, inst, value):
        if self._selecting:
            return
        if self._debounce:
            self._debounce.cancel()
        self._debounce = Clock.schedule_once(self._refresh, 0.18)

    def _on_focus(self, inst, focused):
        if focused:
            Clock.schedule_once(self._refresh, 0.25)
        else:
            # Small delay so a tap on a suggestion registers before we hide
            Clock.schedule_once(lambda dt: self._clear(), 0.25)

    def _refresh(self, dt=None):
        if self._selecting:
            return
        query    = self.field.text.strip().lower()
        all_vals = self.get_items()
        filtered = [v for v in all_vals if query in v.lower()] if query else all_vals
        self._draw(filtered[:10])

    def _draw(self, items):
        self.box.clear_widgets()
        if not items:
            return
        for val in items:
            row = MDCard(
                orientation="vertical",
                size_hint_y=None, height=dp(38),
                md_bg_color=get_color_from_hex("#111827"),
                line_color=get_color_from_hex("#1a2035"),
                radius=[dp(6)], elevation=0,
                ripple_behavior=True,
            )
            row.add_widget(MDLabel(
                text=f"  {val}",
                theme_text_color="Custom",
                text_color=get_color_from_hex(C_TEXT),
                font_size="13sp",
                valign="center",
            ))
            row.bind(on_release=lambda x, v=val: self._select(v))
            self.box.add_widget(row)

    def _select(self, value: str):
        self._selecting = True
        self.field.text = value
        self._clear()
        if self.on_select:
            self.on_select(value)
        Clock.schedule_once(lambda dt: setattr(self, "_selecting", False), 0.2)

    def _clear(self):
        self.box.clear_widgets()

    def destroy(self):
        self._clear()
        try:
            self.field.unbind(text=self._on_text)
            self.field.unbind(focus=self._on_focus)
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════════════════
#  FRIEND CARD
# ══════════════════════════════════════════════════════════════════════════════
def _make_action_btn(label: str, bg_hex: str, text_hex: str, callback, size_hint_x=1):
    """
    Build a simple rectangular action button using MDCard + MDLabel.
    Avoids MDButton tonal style which renders as overlapping circles on Android.
    """
    btn_card = MDCard(
        orientation="vertical",
        size_hint=(size_hint_x, None),
        height=dp(34),
        md_bg_color=get_color_from_hex(bg_hex),
        line_color=(0, 0, 0, 0),
        radius=[dp(8)],
        elevation=0,
        ripple_behavior=True,
    )
    btn_card.add_widget(MDLabel(
        text=label,
        halign="center", valign="center",
        theme_text_color="Custom",
        text_color=get_color_from_hex(text_hex),
        font_size="12sp", bold=True,
    ))
    btn_card.bind(on_release=lambda x: callback())
    return btn_card


def make_friend_card(friend: dict, on_edit, on_delete, on_detail, on_call) -> MDCard:
    color_hex    = AVATAR_COLORS[hash(friend["name"]) % len(AVATAR_COLORS)]
    first_letter = friend["name"][0].upper() if friend["name"] else "?"
    skills_text  = friend.get("skills_list") or ""
    skill_tags   = [s.strip() for s in skills_text.split(",") if s.strip()]
    visible_tags = skill_tags[:3]
    extra        = max(0, len(skill_tags) - 3)
    has_phone    = bool(friend.get("phone", "").strip())

    card = MDCard(
        orientation="vertical",
        padding=dp(14), spacing=dp(8),
        size_hint_y=None, height=dp(162),
        md_bg_color=get_color_from_hex(C_CARD),
        line_color=get_color_from_hex(C_BORDER),
        radius=[dp(16)], elevation=0,
        ripple_behavior=True,
    )
    card.bind(on_release=lambda x: on_detail(friend))

    # Row 1: avatar + name/meta
    top = MDBoxLayout(orientation="horizontal", spacing=dp(12),
                      size_hint_y=None, height=dp(56))

    avatar = MDLabel(
        text=first_letter, halign="center", valign="center",
        theme_text_color="Custom", text_color=(1, 1, 1, 1),
        font_size="20sp", bold=True,
        size_hint=(None, None), size=(dp(46), dp(46)),
    )
    with avatar.canvas.before:
        Color(*get_color_from_hex(color_hex))
        avatar._bg = RoundedRectangle(size=avatar.size, pos=avatar.pos, radius=[dp(13)])
    def _av_upd(inst, _):
        inst._bg.size = inst.size
        inst._bg.pos  = inst.pos
    avatar.bind(size=_av_upd, pos=_av_upd)

    info = MDBoxLayout(orientation="vertical", spacing=dp(2))
    info.add_widget(MDLabel(
        text=friend["name"],
        theme_text_color="Custom",
        text_color=get_color_from_hex(C_TEXT),
        font_size="16sp", bold=True,
        size_hint_y=None, height=dp(26),
    ))
    meta_parts = []
    if friend.get("location"):
        meta_parts.append(f"📍 {friend['location']}")
    if friend.get("phone"):
        meta_parts.append(f"📞 {friend['phone']}")
    info.add_widget(MDLabel(
        text="  ".join(meta_parts) if meta_parts else "No contact info",
        theme_text_color="Custom",
        text_color=get_color_from_hex(C_SECOND),
        font_size="12sp",
        size_hint_y=None, height=dp(20),
    ))
    top.add_widget(avatar)
    top.add_widget(info)

    # Row 2: skill chips
    skills_row = MDBoxLayout(orientation="horizontal", spacing=dp(6),
                              size_hint_y=None, height=dp(26))
    if visible_tags:
        for sk in visible_tags:
            chip = MDLabel(
                text=f" {sk} ", halign="center", valign="center",
                theme_text_color="Custom",
                text_color=get_color_from_hex(C_ACCENT),
                font_size="11sp",
                size_hint=(None, None),
                size=(dp(max(len(sk) * 7 + 16, 40)), dp(22)),
            )
            with chip.canvas.before:
                Color(*get_color_from_hex("#0a2535"))
                chip._bg = RoundedRectangle(size=chip.size, pos=chip.pos, radius=[dp(6)])
            def _chip_upd(inst, _):
                inst._bg.size = inst.size
                inst._bg.pos  = inst.pos
            chip.bind(size=_chip_upd, pos=_chip_upd)
            skills_row.add_widget(chip)
        if extra > 0:
            skills_row.add_widget(MDLabel(
                text=f"+{extra}",
                theme_text_color="Custom",
                text_color=get_color_from_hex("#a78bfa"),
                font_size="11sp",
                size_hint_x=None, width=dp(26),
            ))
    else:
        skills_row.add_widget(MDLabel(
            text="No skills added",
            theme_text_color="Custom",
            text_color=get_color_from_hex(C_MUTED),
            font_size="11sp",
        ))

    # Row 3: EDIT | DELETE | CALL — plain rectangular cards, no MDButton tonal
    btn_row = MDBoxLayout(orientation="horizontal", spacing=dp(6),
                           size_hint_y=None, height=dp(34))

    if has_phone:
        btn_row.add_widget(_make_action_btn("EDIT",   "#0d2535", C_ACCENT,  lambda: on_edit(friend),   size_hint_x=0.34))
        btn_row.add_widget(_make_action_btn("DELETE", "#2a1010", C_DANGER,  lambda: on_delete(friend), size_hint_x=0.34))
        btn_row.add_widget(_make_action_btn("📞 CALL","#0a2510", "#22c55e", lambda: on_call(friend),   size_hint_x=0.32))
    else:
        btn_row.add_widget(_make_action_btn("EDIT",   "#0d2535", C_ACCENT,  lambda: on_edit(friend),   size_hint_x=0.5))
        btn_row.add_widget(_make_action_btn("DELETE", "#2a1010", C_DANGER,  lambda: on_delete(friend), size_hint_x=0.5))

    card.add_widget(top)
    card.add_widget(skills_row)
    card.add_widget(btn_row)
    return card


# ══════════════════════════════════════════════════════════════════════════════
#  DIALOG HELPER
# ══════════════════════════════════════════════════════════════════════════════
def make_dialog(title: str, text: str, buttons: list) -> MDDialog:
    btn_widgets = []
    for lbl, bg, tc, cb in buttons:
        b = MDButton(style="tonal", theme_bg_color="Custom",
                     md_bg_color=get_color_from_hex(bg),
                     on_release=cb)
        b.add_widget(MDButtonText(text=lbl, bold=True,
                                   theme_text_color="Custom",
                                   text_color=get_color_from_hex(tc)))
        btn_widgets.append(b)

    if DIALOG_V2:
        return MDDialog(
            MDDialogHeadlineText(
                text=title, halign="left",
                theme_text_color="Custom",
                text_color=get_color_from_hex(C_TEXT),
            ),
            MDDialogSupportingText(
                text=text, halign="left", markup=True,
                theme_text_color="Custom",
                text_color=get_color_from_hex(C_SECOND),
            ),
            MDDialogButtonContainer(
                MDWidget(),
                *btn_widgets,
                spacing=dp(8),
            ),
        )
    else:
        return MDDialog(title=title, text=text, buttons=btn_widgets)


# ══════════════════════════════════════════════════════════════════════════════
#  SCREENS
# ══════════════════════════════════════════════════════════════════════════════
class LoginScreen(Screen):
    def do_login(self):
        app = MDApp.get_running_app()
        u   = self.ids.login_username.text.strip()
        p   = self.ids.login_password.text
        if not u or not p:
            app.snack("Please fill in all fields.")
            return
        ok, result = app.db.login(u, p)
        if ok:
            app.current_user = result
            app.save_session(result["id"])
            self.ids.login_password.text = ""
            app.root.get_screen("dashboard").on_enter_screen()
            app.root.current = "dashboard"
        else:
            app.snack(result)


class RegisterScreen(Screen):
    def do_register(self):
        app = MDApp.get_running_app()
        u   = self.ids.reg_username.text.strip()
        p   = self.ids.reg_password.text
        c   = self.ids.reg_confirm.text
        if not u or not p or not c:
            app.snack("Please fill in all fields.")
            return
        if p != c:
            app.snack("Passwords do not match!")
            return
        ok, result = app.db.register(u, p)
        if ok:
            app.snack(f"Account created! Welcome, {u}!")
            self.ids.reg_username.text = ""
            self.ids.reg_password.text = ""
            self.ids.reg_confirm.text  = ""
            app.root.current = "login"
        else:
            app.snack(result)


class DashboardScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._skill_ac   = None
        self._loc_ac     = None
        self._active_dlg = None

    def on_enter_screen(self):
        app = MDApp.get_running_app()
        if not app.current_user:
            return
        self.ids.topbar_user.text = f"👤 {app.current_user['username']}"
        self._setup_autocomplete()
        self._load_friends()

    def _setup_autocomplete(self):
        app = MDApp.get_running_app()
        uid = app.current_user["id"]
        if self._skill_ac:
            self._skill_ac.destroy()
        if self._loc_ac:
            self._loc_ac.destroy()
        self._skill_ac = Autocomplete(
            field=self.ids.search_skill,
            suggestion_box=self.ids.skill_suggestions,
            get_items_fn=lambda: app.db.get_all_skills(uid),
            on_select_fn=lambda v: self._load_friends(),
        )
        self._loc_ac = Autocomplete(
            field=self.ids.search_location,
            suggestion_box=self.ids.location_suggestions,
            get_items_fn=lambda: app.db.get_all_locations(uid),
            on_select_fn=lambda v: self._load_friends(),
        )
        self.ids.search_name.bind(text=lambda i, v: self._load_friends())

    def _load_friends(self, *args):
        app = MDApp.get_running_app()
        if not app.current_user:
            return
        uid      = app.current_user["id"]
        search   = self.ids.search_name.text.strip()
        skill    = self.ids.search_skill.text.strip()
        location = self.ids.search_location.text.strip()
        friends  = app.db.get_friends(uid, search=search, skill=skill, location=location)

        total, skills_n, locs_n = app.db.get_stats(uid)
        self.ids.stat_friends_num.text = str(total)
        self.ids.stat_skills_num.text  = str(skills_n)
        self.ids.stat_locs_num.text    = str(locs_n)
        self.ids.results_label.text = (
            f"Results ({len(friends)})"
            if (search or skill or location) else
            f"My Friends ({len(friends)})"
        )

        self.ids.friends_list.clear_widgets()
        if not friends:
            self.ids.friends_list.add_widget(MDLabel(
                text=(
                    "No results found.\nTry different filters."
                    if (search or skill or location) else
                    "No friends yet.\nTap  + ADD  to get started!"
                ),
                halign="center",
                theme_text_color="Custom",
                text_color=get_color_from_hex(C_MUTED),
                size_hint_y=None, height=dp(80),
            ))
            return

        for f in friends:
            card = make_friend_card(
                friend=f,
                on_edit=self._edit_friend,
                on_delete=self._confirm_delete,
                on_detail=self._show_detail,
                on_call=self._call_friend,
            )
            self.ids.friends_list.add_widget(card)

    def _call_friend(self, friend):
        """Open Android phone dialer with friend's number pre-filled."""
        phone = (friend.get("phone") or "").strip()
        if not phone:
            MDApp.get_running_app().snack("No phone number saved.")
            return
        clean = "".join(c for c in phone if c.isdigit() or c == "+")
        try:
            from kivy.utils import platform
            if platform == "android":
                from jnius import autoclass  # type: ignore
                Intent         = autoclass("android.content.Intent")
                Uri            = autoclass("android.net.Uri")
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                intent = Intent(Intent.ACTION_DIAL)
                intent.setData(Uri.parse(f"tel:{clean}"))
                PythonActivity.mActivity.startActivity(intent)
            else:
                import webbrowser
                webbrowser.open(f"tel:{clean}")
        except Exception as e:
            print(f"[Call error] {e}")
            MDApp.get_running_app().snack(f"Opening dialer for {phone}...")

    def go_add_friend(self):
        app = MDApp.get_running_app()
        app.root.get_screen("add_edit").set_mode("add")
        app.root.current = "add_edit"

    def _edit_friend(self, friend):
        app    = MDApp.get_running_app()
        full   = app.db.get_friend(friend["id"], app.current_user["id"])
        skills = app.db.get_friend_skills(friend["id"])
        app.root.get_screen("add_edit").set_mode("edit", full, skills)
        app.root.current = "add_edit"

    def _confirm_delete(self, friend):
        if self._active_dlg:
            self._active_dlg.dismiss()
        self._active_dlg = make_dialog(
            title="Delete Friend",
            text=f"Delete [b]{friend['name']}[/b]?\nThis action cannot be undone.",
            buttons=[
                ("CANCEL", C_ELEVATED, C_SECOND,
                 lambda x: self._active_dlg.dismiss()),
                ("DELETE", "#3a1010", C_DANGER,
                 lambda x: self._do_delete(friend)),
            ],
        )
        self._active_dlg.open()

    def _do_delete(self, friend):
        app = MDApp.get_running_app()
        app.db.delete_friend(friend["id"])
        if self._active_dlg:
            self._active_dlg.dismiss()
        app.snack(f'"{friend["name"]}" deleted.')
        self._load_friends()

    def _show_detail(self, friend):
        app    = MDApp.get_running_app()
        skills = app.db.get_friend_skills(friend["id"])
        if self._active_dlg:
            self._active_dlg.dismiss()
        self._active_dlg = make_dialog(
            title=friend["name"],
            text=(
                f"[b]Phone:[/b] {friend.get('phone') or '—'}\n"
                f"[b]Location:[/b] {friend.get('location') or '—'}\n"
                f"[b]Skills:[/b] {', '.join(skills) if skills else 'None'}\n"
                f"[b]Notes:[/b] {friend.get('notes') or '—'}"
            ),
            buttons=[
                ("CLOSE", C_ELEVATED, C_SECOND,
                 lambda x: self._active_dlg.dismiss()),
                ("EDIT",  "#003540",  C_ACCENT,
                 lambda x: (self._active_dlg.dismiss(), self._edit_friend(friend))),
            ],
        )
        self._active_dlg.open()

    def do_logout(self):
        app = MDApp.get_running_app()
        app.current_user = None
        app.clear_session()
        self.ids.search_name.text     = ""
        self.ids.search_skill.text    = ""
        self.ids.search_location.text = ""
        self.ids.friends_list.clear_widgets()
        app.root.current = "login"
        app.snack("Logged out successfully.")


class AddEditScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mode      = "add"
        self._friend_id = None

    def on_kv_post(self, base_widget):
        # Delay chip building so Window.width is known
        Clock.schedule_once(lambda dt: self._build_quick_chips(), 0.1)

    def _build_quick_chips(self):
        """
        Pack skill chips into rows that fit the screen width.
        No scrolling needed — chips wrap onto new lines.
        """
        container = self.ids.chips_container
        container.clear_widgets()

        # Use actual window width; fallback to 360dp
        screen_w  = Window.width if Window.width > 10 else dp(360)
        padding   = dp(36)
        gap       = dp(8)
        available = screen_w - padding

        # Measure each chip
        chip_data = [(sk, dp(len(sk) * 8 + 28)) for sk in QUICK_SKILLS]

        # Greedy row packing
        rows   = []
        row    = []
        used_w = 0.0
        for sk, w in chip_data:
            need = w if not row else w + gap
            if row and used_w + need > available:
                rows.append(row)
                row    = [(sk, w)]
                used_w = w
            else:
                row.append((sk, w))
                used_w += need
        if row:
            rows.append(row)

        for row_chips in rows:
            row_box = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None, height=dp(40),
                spacing=dp(8),
            )
            for sk, w in row_chips:
                btn = MDButton(
                    style="outlined",
                    size_hint=(None, None),
                    size=(w, dp(36)),
                    theme_bg_color="Custom",
                    md_bg_color=get_color_from_hex("#0a1a25"),
                    line_color=get_color_from_hex(C_ACCENT),
                )
                btn.add_widget(MDButtonText(
                    text=sk, font_size="12sp",
                    theme_text_color="Custom",
                    text_color=get_color_from_hex(C_ACCENT),
                ))
                btn.bind(on_release=lambda x, s=sk: self._add_quick_skill(s))
                row_box.add_widget(btn)
            container.add_widget(row_box)

    def _add_quick_skill(self, skill: str):
        field = self.ids.f_skills
        parts = [s.strip() for s in field.text.split(",") if s.strip()]
        if skill not in parts:
            parts.append(skill)
            field.text = ", ".join(parts)

    def set_mode(self, mode: str, friend=None, skills=None):
        self._mode      = mode
        self._friend_id = friend["id"] if friend else None
        self.ids.save_btn_text.text = "SAVE FRIEND" if mode == "add" else "UPDATE FRIEND"
        self.ids.form_title.text    = "Add Friend"  if mode == "add" else "Edit Friend"
        self.ids.f_name.text     = "" if mode == "add" else (friend.get("name")     or "")
        self.ids.f_phone.text    = "" if mode == "add" else (friend.get("phone")    or "")
        self.ids.f_location.text = "" if mode == "add" else (friend.get("location") or "")
        self.ids.f_skills.text   = "" if mode == "add" else ", ".join(skills or [])
        self.ids.f_notes.text    = "" if mode == "add" else (friend.get("notes")    or "")

    def do_save(self):
        app  = MDApp.get_running_app()
        name = self.ids.f_name.text.strip()
        if not name:
            app.snack("Name is required!")
            return
        uid      = app.current_user["id"]
        phone    = self.ids.f_phone.text.strip()
        location = self.ids.f_location.text.strip()
        notes    = self.ids.f_notes.text.strip()
        skills   = [s.strip() for s in self.ids.f_skills.text.split(",") if s.strip()]
        if self._mode == "add":
            app.db.add_friend(uid, name, phone, location, notes, skills)
            app.snack(f'"{name}" added!')
        else:
            app.db.update_friend(self._friend_id, name, phone, location, notes, skills)
            app.snack(f'"{name}" updated!')
        self.go_back()

    def go_back(self):
        app = MDApp.get_running_app()
        app.root.get_screen("dashboard").on_enter_screen()
        app.root.current = "dashboard"


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════════════════════
class SkillBondApp(MDApp):

    current_user = None

    def build(self):
        self.theme_cls.theme_style     = "Dark"
        self.theme_cls.primary_palette = "Cyan"
        self.theme_cls.accent_palette  = "DeepPurple"
        self.db_path      = os.path.join(self.user_data_dir, "skillbond.db")
        self.session_path = os.path.join(self.user_data_dir, "session.json")
        self.db = Database(self.db_path)
        return SkillBondSM(transition=FadeTransition(duration=0.2))

    def on_start(self):
        """Auto-login using saved session (by user_id — no password stored)."""
        session = self._load_session()
        if session and "user_id" in session:
            user = self._fetch_user_by_id(session["user_id"])
            if user:
                self.current_user = user
                dash = self.root.get_screen("dashboard")
                dash.on_enter_screen()
                self.root.current = "dashboard"
                return
        self.root.current = "login"

    # ── Session helpers ───────────────────────────────────────────────────────

    def save_session(self, user_id: int):
        try:
            with open(self.session_path, "w") as f:
                json.dump({"user_id": user_id}, f)
        except Exception as e:
            print(f"[Session save] {e}")

    def _load_session(self):
        try:
            if not os.path.exists(self.session_path):
                return None
            with open(self.session_path) as f:
                return json.load(f)
        except Exception:
            return None

    def clear_session(self):
        try:
            if os.path.exists(self.session_path):
                os.remove(self.session_path)
        except Exception as e:
            print(f"[Session clear] {e}")

    def _fetch_user_by_id(self, user_id: int):
        """Load user row directly by ID — safe for auto-login."""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM users WHERE id=?", (user_id,)
            ).fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception as e:
            print(f"[FetchUser] {e}")
            return None

    def snack(self, message: str):
        try:
            MDSnackbar(
                MDSnackbarText(text=message),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.92,
                duration=2.5,
                md_bg_color=get_color_from_hex(C_ELEVATED),
            ).open()
        except Exception as e:
            print(f"[Snack] {message}  ({e})")


if __name__ == "__main__":
    SkillBondApp().run()
