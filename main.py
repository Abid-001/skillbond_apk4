"""
SkillBond - Android APK
Built with Kivy 2.3.0 + KivyMD 2.0.1 + Python 3.10.11
Dark modern theme | Multi-user | Local SQLite | Live autocomplete

KivyMD 2.0.1 breaking changes handled:
  - MDRaisedButton / MDFlatButton  → MDButton (style="filled" / "text" / "tonal")
  - MDIconButton                   → MDIconButton (theme_icon_color instead of theme_text_color)
  - MDDialog                       → component-based (MDDialogHeadlineText, MDDialogSupportingText, MDDialogButtonContainer)
  - MDSnackbar                     → MDSnackbar(MDSnackbarText(...), y=dp(24), ...)
  - MDTextField                    → text_color_normal + text_color_focus (both required)
  - MDButton text                  → must use MDButtonText child widget
"""

import os
import sys

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, RoundedRectangle

from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.widget import MDWidget

# KivyMD 2.0.1 dialog sub-components — try/except for build compatibility
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

# ── Palette constants ─────────────────────────────────────────────────────────
C_BG       = "#080b12"
C_CARD     = "#0e1220"
C_ELEVATED = "#151c2c"
C_ACCENT   = "#00d4ff"
C_ACCENT2  = "#7c3aed"
C_TEXT     = "#f0f4ff"
C_SECOND   = "#8892a4"
C_MUTED    = "#4a5568"
C_HINT     = "#8892a4"  # visible hint text color for Android
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

# ── KV string ─────────────────────────────────────────────────────────────────
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
            height: dp(190)
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
                height: dp(38)

            MDLabel:
                text: 'Find the Right Friend, Fast'
                halign: 'center'
                theme_text_color: 'Custom'
                text_color: hex("#8892a4")
                font_size: '12sp'
                size_hint_y: None
                height: dp(22)

        MDWidget:
            size_hint_y: None
            height: dp(18)

        MDCard:
            orientation: 'vertical'
            padding: dp(24)
            spacing: dp(10)
            size_hint: 1, None
            height: dp(270)
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
                icon_left: "account"
                size_hint_y: None
                height: dp(54)

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
                icon_left: "lock"
                size_hint_y: None
                height: dp(54)

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
            spacing: dp(16)
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
                padding: dp(24)
                spacing: dp(8)
                size_hint: 1, None
                height: dp(440)
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
                    icon_left: "account"
                    size_hint_y: None
                    height: dp(54)

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
                    icon_left: "lock"
                    size_hint_y: None
                    height: dp(54)

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
                    icon_left: "shield-check"
                    size_hint_y: None
                    height: dp(54)

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

        # Top bar
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

                # Stats row ───────────────────────────────────────────────────
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

                # Search card ─────────────────────────────────────────────────
                MDCard:
                    orientation: 'vertical'
                    padding: [dp(14), dp(12)]
                    spacing: dp(6)
                    size_hint_y: None
                    height: dp(288)
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
                        icon_left: "magnify"
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
                        icon_left: "tag"
                        size_hint_y: None
                        height: dp(50)

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
                        icon_left: "map-marker"
                        size_hint_y: None
                        height: dp(50)

                # Results header ──────────────────────────────────────────────
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

                # Friend cards container ───────────────────────────────────────
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

            MDCard:
                orientation: 'vertical'
                padding: dp(20)
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
                    icon_left: "account"
                    size_hint_y: None
                    height: dp(54)

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
                    icon_left: "phone"
                    size_hint_y: None
                    height: dp(54)

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
                    icon_left: "map-marker"
                    size_hint_y: None
                    height: dp(54)

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
                    icon_left: "tag-multiple"
                    size_hint_y: None
                    height: dp(54)

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
                    max_height: dp(78)
                    theme_text_color: "Custom"
                    text_color_normal: hex("#f0f4ff")
                    text_color_focus: hex("#f0f4ff")
                    hint_text_color_normal: hex("#8892a4")
                    hint_text_color_focus: hex("#8892a4")
                    line_color_normal: hex("#2a3a55")
                    line_color_focus: hex("#00d4ff")
                    icon_left: "note-text"
                    size_hint_y: None
                    height: dp(78)

            MDLabel:
                text: 'Quick Add Skills:'
                theme_text_color: 'Custom'
                text_color: hex("#8892a4")
                font_size: '13sp'
                bold: True
                size_hint_y: None
                height: dp(24)

            ScrollView:
                size_hint_y: None
                height: dp(44)
                do_scroll_y: False
                bar_width: 0
                MDBoxLayout:
                    id: quick_chips_1
                    orientation: 'horizontal'
                    size_hint_x: None
                    width: self.minimum_width
                    height: dp(40)
                    spacing: dp(8)

            ScrollView:
                size_hint_y: None
                height: dp(44)
                do_scroll_y: False
                bar_width: 0
                MDBoxLayout:
                    id: quick_chips_2
                    orientation: 'horizontal'
                    size_hint_x: None
                    width: self.minimum_width
                    height: dp(40)
                    spacing: dp(8)

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
#  AUTOCOMPLETE  (fixes "suggestions not showing while typing")
# ══════════════════════════════════════════════════════════════════════════════
class Autocomplete:
    """
    Attaches a live-filtering dropdown menu to an MDTextField.

    How it fixes the bug:
    - Binds to `text` property → fires on EVERY single keystroke
    - 120ms Clock debounce → avoids rebuilding on each individual character
    - Full dismiss → rebuild → reopen cycle → menu always shows fresh data
    - Also binds to `focus` → shows all suggestions when field is first tapped
    """

    def __init__(self, field: MDTextField, get_items_fn, on_select_fn=None):
        self.field      = field
        self.get_items  = get_items_fn   # callable returning list[str]
        self.on_select  = on_select_fn   # optional callback after selection
        self.menu       = None
        self._debounce  = None
        self._selecting = False

        field.bind(text=self._on_text)
        field.bind(focus=self._on_focus)

    def _on_text(self, instance, value):
        """Key fix: fires on every keystroke, not just focus change."""
        if self._debounce:
            self._debounce.cancel()
        self._debounce = Clock.schedule_once(self._refresh, 0.12)

    def _on_focus(self, instance, focused):
        if focused:
            Clock.schedule_once(self._refresh, 0.28)
        else:
            Clock.schedule_once(lambda dt: self._close(), 0.3)

    def _refresh(self, dt=None):
        if self._selecting:
            return

        query    = self.field.text.strip().lower()
        all_vals = self.get_items()

        # Empty query → show everything; otherwise substring filter
        filtered = (
            [v for v in all_vals if query in v.lower()]
            if query else all_vals
        )

        self._close()

        if not filtered or not self.field.focus:
            return

        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": v,
                "theme_text_color": "Custom",
                "text_color": get_color_from_hex(C_TEXT),
                "on_release": lambda x=v: self._select(x),
            }
            for v in filtered[:14]
        ]

        self.menu = MDDropdownMenu(
            caller=self.field,
            items=menu_items,
            width_mult=4,
            max_height=dp(240),
            elevation=8,
            background_color=get_color_from_hex("#111827"),
            border_margin=dp(4),
            opening_time=0.12,
        )
        self.menu.open()

    def _select(self, value: str):
        self._selecting = True
        self.field.text = value
        self._close()
        if self.on_select:
            self.on_select(value)
        Clock.schedule_once(lambda dt: setattr(self, "_selecting", False), 0.15)

    def _close(self):
        if self.menu:
            try:
                self.menu.dismiss()
            except Exception:
                pass
            self.menu = None

    def destroy(self):
        self._close()
        try:
            self.field.unbind(text=self._on_text)
            self.field.unbind(focus=self._on_focus)
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════════════════
#  FRIEND CARD  (built in Python, not KV)
# ══════════════════════════════════════════════════════════════════════════════
def make_friend_card(friend: dict, on_edit, on_delete, on_detail) -> MDCard:
    """Dynamically build one friend card widget."""
    color_hex    = AVATAR_COLORS[hash(friend["name"]) % len(AVATAR_COLORS)]
    first_letter = friend["name"][0].upper() if friend["name"] else "?"
    skills_text  = friend.get("skills_list") or ""
    skill_tags   = [s.strip() for s in skills_text.split(",") if s.strip()]
    visible_tags = skill_tags[:3]
    extra        = max(0, len(skill_tags) - 3)

    card = MDCard(
        orientation="vertical",
        padding=dp(14), spacing=dp(8),
        size_hint_y=None, height=dp(158),
        md_bg_color=get_color_from_hex(C_CARD),
        line_color=get_color_from_hex(C_BORDER),
        radius=[dp(16)], elevation=0,
        ripple_behavior=True,
    )
    card.bind(on_release=lambda x: on_detail(friend))

    # ── Row 1: avatar + name/meta ────────────────────────────────────────────
    top = MDBoxLayout(orientation="horizontal", spacing=dp(12),
                      size_hint_y=None, height=dp(58))

    avatar = MDLabel(
        text=first_letter, halign="center", valign="center",
        theme_text_color="Custom", text_color=(1, 1, 1, 1),
        font_size="20sp", bold=True,
        size_hint=(None, None), size=(dp(46), dp(46)),
    )
    with avatar.canvas.before:
        Color(*get_color_from_hex(color_hex))
        avatar._bg = RoundedRectangle(
            size=avatar.size, pos=avatar.pos, radius=[dp(13)]
        )
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

    # ── Row 2: skill chips ───────────────────────────────────────────────────
    skills_row = MDBoxLayout(orientation="horizontal", spacing=dp(6),
                              size_hint_y=None, height=dp(28))
    if visible_tags:
        for sk in visible_tags:
            chip = MDLabel(
                text=f" {sk} ", halign="center", valign="center",
                theme_text_color="Custom",
                text_color=get_color_from_hex(C_ACCENT),
                font_size="12sp",
                size_hint=(None, None),
                size=(dp(max(len(sk) * 7 + 18, 42)), dp(24)),
            )
            with chip.canvas.before:
                Color(*get_color_from_hex("#0a2535"))
                chip._bg = RoundedRectangle(
                    size=chip.size, pos=chip.pos, radius=[dp(8)]
                )
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
                font_size="12sp",
                size_hint_x=None, width=dp(28),
            ))
    else:
        skills_row.add_widget(MDLabel(
            text="No skills added",
            theme_text_color="Custom",
            text_color=get_color_from_hex(C_MUTED),
            font_size="12sp",
        ))

    # ── Row 3: action buttons ────────────────────────────────────────────────
    btn_row = MDBoxLayout(orientation="horizontal", spacing=dp(8),
                           size_hint_y=None, height=dp(36))

    # KivyMD 2.0.1: MDButton with MDButtonText child
    btn_edit = MDButton(style="tonal", size_hint_x=0.5,
                         theme_bg_color="Custom",
                         md_bg_color=get_color_from_hex("#0d1f2d"))
    btn_edit.add_widget(MDButtonText(text="EDIT", bold=True,
                                      theme_text_color="Custom",
                                      text_color=get_color_from_hex(C_ACCENT)))
    btn_edit.bind(on_release=lambda x: on_edit(friend))

    btn_del = MDButton(style="tonal", size_hint_x=0.5,
                        theme_bg_color="Custom",
                        md_bg_color=get_color_from_hex("#2a1515"))
    btn_del.add_widget(MDButtonText(text="DELETE", bold=True,
                                     theme_text_color="Custom",
                                     text_color=get_color_from_hex(C_DANGER)))
    btn_del.bind(on_release=lambda x: on_delete(friend))

    btn_row.add_widget(btn_edit)
    btn_row.add_widget(btn_del)

    card.add_widget(top)
    card.add_widget(skills_row)
    card.add_widget(btn_row)
    return card


# ══════════════════════════════════════════════════════════════════════════════
#  DIALOG HELPER  (KivyMD 2.0.1 component-based API)
# ══════════════════════════════════════════════════════════════════════════════
def make_dialog(title: str, text: str, buttons: list) -> MDDialog:
    """
    buttons = list of (label, bg_hex, text_hex, on_release_callback)
    Works with both KivyMD 2.0.1 (component API) and older builds.
    """
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
        # Fallback: simple MDDialog with title/text kwargs
        return MDDialog(
            title=title,
            text=text,
            buttons=btn_widgets,
        )


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

        # Destroy previous (important on re-login)
        if self._skill_ac:
            self._skill_ac.destroy()
        if self._loc_ac:
            self._loc_ac.destroy()

        self._skill_ac = Autocomplete(
            field=self.ids.search_skill,
            get_items_fn=lambda: app.db.get_all_skills(uid),
            on_select_fn=lambda v: self._load_friends(),
        )
        self._loc_ac = Autocomplete(
            field=self.ids.search_location,
            get_items_fn=lambda: app.db.get_all_locations(uid),
            on_select_fn=lambda v: self._load_friends(),
        )
        # Name: live filter on every keystroke
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
            )
            self.ids.friends_list.add_widget(card)

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
        app        = MDApp.get_running_app()
        skills     = app.db.get_friend_skills(friend["id"])
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
                ("CLOSE",  C_ELEVATED, C_SECOND,
                 lambda x: self._active_dlg.dismiss()),
                ("EDIT",   "#003540",  C_ACCENT,
                 lambda x: (self._active_dlg.dismiss(), self._edit_friend(friend))),
            ],
        )
        self._active_dlg.open()

    def do_logout(self):
        app = MDApp.get_running_app()
        app.current_user = None
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
        self._build_quick_chips()

    def _build_quick_chips(self):
        row1 = self.ids.quick_chips_1
        row2 = self.ids.quick_chips_2
        row1.clear_widgets()
        row2.clear_widgets()
        half = len(QUICK_SKILLS) // 2

        for i, sk in enumerate(QUICK_SKILLS):
            chip_width = dp(len(sk) * 9 + 32)
            btn = MDButton(
                style="outlined",
                size_hint=(None, None),
                size=(chip_width, dp(38)),
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
            (row1 if i < half else row2).add_widget(btn)

    def _add_quick_skill(self, skill: str):
        field = self.ids.f_skills
        parts = [s.strip() for s in field.text.split(",") if s.strip()]
        if skill not in parts:
            parts.append(skill)
            field.text = ", ".join(parts)

    def set_mode(self, mode: str, friend=None, skills=None):
        self._mode      = mode
        self._friend_id = friend["id"] if friend else None
        # Update button text via the MDButtonText child id in KV
        self.ids.save_btn_text.text = "SAVE FRIEND" if mode == "add" else "UPDATE FRIEND"
        self.ids.form_title.text    = "Add Friend"   if mode == "add" else "Edit Friend"
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
        db_path = os.path.join(self.user_data_dir, "skillbond.db")
        self.db = Database(db_path)
        return SkillBondSM(transition=FadeTransition(duration=0.2))

    def snack(self, message: str):
        """KivyMD 2.0.1 Snackbar — uses y= instead of pos_hint for vertical position."""
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
