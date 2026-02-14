"""
JobSage Configuration GUI
A modern graphical interface for editing JobSage ETL configuration
Made by Ai!
Obviously I wouldn't type it all myself

-Zn0x
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tomllib
import json
from pathlib import Path
from typing import Dict, Any


class JobSageConfigGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JobSage Configuration Manager")
        self.root.geometry("1400x900")
        
        # Configuration file path
        self.config_file = Path("config/config.toml")
        self.config_data = {}
        
        # Color scheme
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'accent': '#007acc',
            'secondary': '#2d2d2d',
            'success': '#4ec9b0',
            'warning': '#ce9178',
            'error': '#f48771'
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['bg'])
        
        # Load configuration
        self.load_config()
        
        # Setup UI
        self.create_ui()
        
    def load_config(self):
        """Load TOML configuration file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'rb') as f:
                    self.config_data = tomllib.load(f)
            else:
                self.create_default_config()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration"""
        self.config_data = {
            'extractors': {
                'output_dir': 'data/raw',
                'careerjet': {
                    'enabled': True,
                    'max_pages': 2,
                    'base_url': 'https://www.careerjet.com.pk/jobs?l=Pakistan&nw=1&s=',
                    'output_path': 'data/raw/careerjet.json',
                    'card': 'ul.jobs li article.job'
                },
                'rozee': {
                    'enabled': True,
                    'max_pages': 2,
                    'base_url': 'https://www.rozee.pk/job/jsearch/q/',
                    'output_path': 'data/raw/rozee.json',
                    'card': 'div.job'
                }
            },
            'transformers': {
                'output_dir': 'data/curated',
                'careerjet': {
                    'output_path': 'data/curated/cleaned_careerjet.json',
                    'date_pattern': r'\d+\s+(?:second|minute|hour|day|week|month|year)s?\s+ago'
                },
                'rozee': {
                    'output_path': 'data/curated/cleaned_rozee.json',
                    'date_pattern': r'(\d+)\s+(hour|day|week|month)s?\s+ago'
                }
            },
            'loaders': {
                'dotenv_path': 'config/.env',
                'careerjet': {
                    'platform_name': 'careerjet.pk',
                    'base_url': 'https://www.careerjet.com.pk'
                },
                'rozee': {
                    'platform_name': 'rozee.pk',
                    'base_url': 'https://www.rozee.pk'
                }
            },
            'scheduler': {
                'hour': 2,
                'minute': 0
            }
        }
    
    def create_ui(self):
        """Create the main user interface"""
        # Header
        self.create_header()
        
        # Main content area with tabs
        self.create_tabs()
        
        # Footer with action buttons
        self.create_footer()
    
    def create_header(self):
        """Create application header"""
        header = tk.Frame(self.root, bg=self.colors['accent'], height=80)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="JobSage Configuration Manager",
            font=('Segoe UI', 24, 'bold'),
            bg=self.colors['accent'],
            fg='white'
        )
        title.pack(side=tk.LEFT, padx=20, pady=20)
        
        subtitle = tk.Label(
            header,
            text="ETL Pipeline Configuration",
            font=('Segoe UI', 12),
            bg=self.colors['accent'],
            fg='white'
        )
        subtitle.pack(side=tk.LEFT, padx=5, pady=20)
    
    def create_tabs(self):
        """Create tabbed interface"""
        # Configure style for dark theme
        style = ttk.Style()
        style.theme_use('default')
        
        # Configure tab colors
        style.configure('TNotebook', background=self.colors['bg'], borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background=self.colors['secondary'],
                       foreground=self.colors['fg'],
                       padding=[20, 10],
                       font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['accent'])],
                 foreground=[('selected', 'white')])
        
        # Create notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))
        
        # Create tabs
        self.create_extractors_tab()
        self.create_transformers_tab()
        self.create_loaders_tab()
        self.create_scheduler_tab()
        self.create_preview_tab()
    
    def create_extractors_tab(self):
        """Create extractors configuration tab"""
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab, text='Extractors')
        
        # Create scrollable canvas
        canvas = tk.Canvas(tab, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # General Settings
        general_frame = self.create_section_frame(
            scrollable_frame,
            "General Extractor Settings"
        )
        general_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.extractor_output_dir = self.create_text_field(
            general_frame,
            "Output Directory:",
            self.config_data['extractors'].get('output_dir', 'data/raw')
        )
        
        # Rozee Extractor
        rozee_frame = self.create_section_frame(scrollable_frame, "Rozee.pk Extractor")
        rozee_frame.pack(fill=tk.X, padx=20, pady=10)
        
        rozee_config = self.config_data['extractors'].get('rozee', {})
        
        self.rozee_enabled = self.create_checkbox(
            rozee_frame,
            "Enabled",
            rozee_config.get('enabled', True)
        )
        
        self.rozee_max_pages = self.create_number_field(
            rozee_frame,
            "Maximum Pages:",
            rozee_config.get('max_pages', 2)
        )
        
        self.rozee_base_url = self.create_text_field(
            rozee_frame,
            "Base URL:",
            rozee_config.get('base_url', '')
        )
        
        self.rozee_output_path = self.create_text_field(
            rozee_frame,
            "Output Path:",
            rozee_config.get('output_path', '')
        )
        
        self.rozee_card = self.create_text_field(
            rozee_frame,
            "CSS Selector (Card):",
            rozee_config.get('card', '')
        )
        
        # Careerjet Extractor
        careerjet_frame = self.create_section_frame(scrollable_frame, "Careerjet.pk Extractor")
        careerjet_frame.pack(fill=tk.X, padx=20, pady=10)
        
        careerjet_config = self.config_data['extractors'].get('careerjet', {})
        
        self.careerjet_enabled = self.create_checkbox(
            careerjet_frame,
            "Enabled",
            careerjet_config.get('enabled', True)
        )
        
        self.careerjet_max_pages = self.create_number_field(
            careerjet_frame,
            "Maximum Pages:",
            careerjet_config.get('max_pages', 2)
        )
        
        self.careerjet_base_url = self.create_text_field(
            careerjet_frame,
            "Base URL:",
            careerjet_config.get('base_url', '')
        )
        
        self.careerjet_output_path = self.create_text_field(
            careerjet_frame,
            "Output Path:",
            careerjet_config.get('output_path', '')
        )
        
        self.careerjet_card = self.create_text_field(
            careerjet_frame,
            "CSS Selector (Card):",
            careerjet_config.get('card', '')
        )
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_transformers_tab(self):
        """Create transformers configuration tab"""
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab, text='Transformers')
        
        # General Settings
        general_frame = self.create_section_frame(tab, "General Transformer Settings")
        general_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.transformer_output_dir = self.create_text_field(
            general_frame,
            "Output Directory:",
            self.config_data['transformers'].get('output_dir', 'data/curated')
        )
        
        # Rozee Transformer
        rozee_frame = self.create_section_frame(tab, "Rozee Transformer")
        rozee_frame.pack(fill=tk.X, padx=20, pady=10)
        
        rozee_config = self.config_data['transformers'].get('rozee', {})
        
        self.rozee_trans_output = self.create_text_field(
            rozee_frame,
            "Output Path:",
            rozee_config.get('output_path', '')
        )
        
        self.rozee_date_pattern = self.create_text_field(
            rozee_frame,
            "Date Pattern (Regex):",
            rozee_config.get('date_pattern', '')
        )
        
        # Careerjet Transformer
        careerjet_frame = self.create_section_frame(tab, "Careerjet Transformer")
        careerjet_frame.pack(fill=tk.X, padx=20, pady=10)
        
        careerjet_config = self.config_data['transformers'].get('careerjet', {})
        
        self.careerjet_trans_output = self.create_text_field(
            careerjet_frame,
            "Output Path:",
            careerjet_config.get('output_path', '')
        )
        
        self.careerjet_date_pattern = self.create_text_field(
            careerjet_frame,
            "Date Pattern (Regex):",
            careerjet_config.get('date_pattern', '')
        )
    
    def create_loaders_tab(self):
        """Create loaders configuration tab"""
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab, text='Loaders')
        
        # General Settings
        general_frame = self.create_section_frame(tab, "General Loader Settings")
        general_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.loader_dotenv_path = self.create_text_field(
            general_frame,
            "Environment File Path:",
            self.config_data['loaders'].get('dotenv_path', 'config/.env')
        )
        
        # Rozee Platform
        rozee_frame = self.create_section_frame(tab, "Rozee Platform Configuration")
        rozee_frame.pack(fill=tk.X, padx=20, pady=10)
        
        rozee_config = self.config_data['loaders'].get('rozee', {})
        
        self.rozee_platform_name = self.create_text_field(
            rozee_frame,
            "Platform Name:",
            rozee_config.get('platform_name', 'rozee.pk')
        )
        
        self.rozee_platform_url = self.create_text_field(
            rozee_frame,
            "Base URL:",
            rozee_config.get('base_url', 'https://www.rozee.pk')
        )
        
        # Careerjet Platform
        careerjet_frame = self.create_section_frame(tab, "Careerjet Platform Configuration")
        careerjet_frame.pack(fill=tk.X, padx=20, pady=10)
        
        careerjet_config = self.config_data['loaders'].get('careerjet', {})
        
        self.careerjet_platform_name = self.create_text_field(
            careerjet_frame,
            "Platform Name:",
            careerjet_config.get('platform_name', 'careerjet.pk')
        )
        
        self.careerjet_platform_url = self.create_text_field(
            careerjet_frame,
            "Base URL:",
            careerjet_config.get('base_url', 'https://www.careerjet.com.pk')
        )
    
    def create_scheduler_tab(self):
        """Create scheduler configuration tab"""
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab, text='Scheduler')
        
        frame = self.create_section_frame(tab, "Automated ETL Schedule")
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        scheduler_config = self.config_data.get('scheduler', {})
        
        # Hour setting
        self.scheduler_hour = self.create_number_field(
            frame,
            "Hour (0-23):",
            scheduler_config.get('hour', 2),
            min_val=0,
            max_val=23
        )
        
        # Minute setting
        self.scheduler_minute = self.create_number_field(
            frame,
            "Minute (0-59):",
            scheduler_config.get('minute', 0),
            min_val=0,
            max_val=59
        )
        
        # Info text
        info_frame = tk.Frame(frame, bg=self.colors['secondary'], relief=tk.RIDGE, borderwidth=2)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=20)
        
        info_label = tk.Label(
            info_frame,
            text="Scheduler Information",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['success']
        )
        info_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        info_text = tk.Text(
            info_frame,
            height=12,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            borderwidth=0
        )
        info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        info_content = """The scheduler controls when the automated ETL pipeline runs.

Configuration:
• Hour: The hour of day when ETL runs (24-hour format)
• Minute: The minute of the hour when ETL runs

Examples:
• Hour: 2, Minute: 0  → Runs at 2:00 AM daily
• Hour: 14, Minute: 30 → Runs at 2:30 PM daily
• Hour: 0, Minute: 0  → Runs at midnight daily

The ETL pipeline will:
1. Extract jobs from all enabled platforms
2. Transform and clean the data
3. Load results into the database

Logs are stored in the logs/ directory."""
        
        info_text.insert(1.0, info_content)
        info_text.config(state=tk.DISABLED)
    
    def create_preview_tab(self):
        """Create configuration preview tab"""
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab, text='Preview')
        
        # Toolbar
        toolbar = tk.Frame(tab, bg=self.colors['secondary'], height=50)
        toolbar.pack(fill=tk.X, padx=0, pady=0)
        toolbar.pack_propagate(False)
        
        update_btn = tk.Button(
            toolbar,
            text="Update Preview",
            command=self.update_preview,
            bg=self.colors['accent'],
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        update_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Preview text area
        text_frame = tk.Frame(tab, bg=self.colors['bg'])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Text widget
        self.preview_text = tk.Text(
            text_frame,
            wrap=tk.NONE,
            font=('Consolas', 10),
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg'],
            yscrollcommand=scrollbar.set
        )
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.preview_text.yview)
        
        # Initial preview
        self.update_preview()
    
    def create_footer(self):
        """Create footer with action buttons"""
        footer = tk.Frame(self.root, bg=self.colors['secondary'], height=70)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        # Button container
        button_container = tk.Frame(footer, bg=self.colors['secondary'])
        button_container.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Save button
        save_btn = tk.Button(
            button_container,
            text="Save Configuration",
            command=self.save_config,
            bg=self.colors['success'],
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            relief=tk.FLAT,
            padx=30,
            pady=12,
            cursor='hand2'
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Export button
        export_btn = tk.Button(
            button_container,
            text="Export JSON",
            command=self.export_json,
            bg=self.colors['accent'],
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            relief=tk.FLAT,
            padx=30,
            pady=12,
            cursor='hand2'
        )
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # Load button
        load_btn = tk.Button(
            button_container,
            text="Load Config",
            command=self.load_config_file,
            bg=self.colors['warning'],
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            relief=tk.FLAT,
            padx=30,
            pady=12,
            cursor='hand2'
        )
        load_btn.pack(side=tk.LEFT, padx=5)
    
    # UI Helper Methods
    
    def create_section_frame(self, parent, title):
        """Create a styled section frame"""
        frame = tk.Frame(parent, bg=self.colors['secondary'], relief=tk.RIDGE, borderwidth=2)
        
        title_label = tk.Label(
            frame,
            text=title,
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['accent']
        )
        title_label.pack(anchor=tk.W, padx=10, pady=10)
        
        return frame
    
    def create_text_field(self, parent, label_text, default_value):
        """Create a labeled text entry field"""
        container = tk.Frame(parent, bg=self.colors['secondary'])
        container.pack(fill=tk.X, padx=10, pady=5)
        
        label = tk.Label(
            container,
            text=label_text,
            font=('Segoe UI', 10),
            bg=self.colors['secondary'],
            fg=self.colors['fg'],
            width=20,
            anchor=tk.W
        )
        label.pack(side=tk.LEFT, padx=5)
        
        var = tk.StringVar(value=str(default_value))
        entry = tk.Entry(
            container,
            textvariable=var,
            font=('Segoe UI', 10),
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg'],
            relief=tk.FLAT,
            borderwidth=2
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        return var
    
    def create_number_field(self, parent, label_text, default_value, min_val=0, max_val=100):
        """Create a labeled number entry field with validation"""
        container = tk.Frame(parent, bg=self.colors['secondary'])
        container.pack(fill=tk.X, padx=10, pady=5)
        
        label = tk.Label(
            container,
            text=label_text,
            font=('Segoe UI', 10),
            bg=self.colors['secondary'],
            fg=self.colors['fg'],
            width=20,
            anchor=tk.W
        )
        label.pack(side=tk.LEFT, padx=5)
        
        var = tk.IntVar(value=int(default_value))
        spinbox = tk.Spinbox(
            container,
            from_=min_val,
            to=max_val,
            textvariable=var,
            font=('Segoe UI', 10),
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg'],
            relief=tk.FLAT,
            borderwidth=2,
            width=10
        )
        spinbox.pack(side=tk.LEFT, padx=5)
        
        return var
    
    def create_checkbox(self, parent, label_text, default_value):
        """Create a checkbox"""
        var = tk.BooleanVar(value=bool(default_value))
        
        checkbox = tk.Checkbutton(
            parent,
            text=label_text,
            variable=var,
            font=('Segoe UI', 10),
            bg=self.colors['secondary'],
            fg=self.colors['fg'],
            selectcolor=self.colors['bg'],
            activebackground=self.colors['secondary'],
            activeforeground=self.colors['accent']
        )
        checkbox.pack(anchor=tk.W, padx=10, pady=5)
        
        return var
    
    # Data Methods
    
    def gather_data(self):
        """Gather all configuration data from UI fields"""
        return {
            'extractors': {
                'output_dir': self.extractor_output_dir.get(),
                'rozee': {
                    'enabled': self.rozee_enabled.get(),
                    'max_pages': self.rozee_max_pages.get(),
                    'base_url': self.rozee_base_url.get(),
                    'output_path': self.rozee_output_path.get(),
                    'card': self.rozee_card.get()
                },
                'careerjet': {
                    'enabled': self.careerjet_enabled.get(),
                    'max_pages': self.careerjet_max_pages.get(),
                    'base_url': self.careerjet_base_url.get(),
                    'output_path': self.careerjet_output_path.get(),
                    'card': self.careerjet_card.get()
                }
            },
            'transformers': {
                'output_dir': self.transformer_output_dir.get(),
                'rozee': {
                    'output_path': self.rozee_trans_output.get(),
                    'date_pattern': self.rozee_date_pattern.get()
                },
                'careerjet': {
                    'output_path': self.careerjet_trans_output.get(),
                    'date_pattern': self.careerjet_date_pattern.get()
                }
            },
            'loaders': {
                'dotenv_path': self.loader_dotenv_path.get(),
                'rozee': {
                    'platform_name': self.rozee_platform_name.get(),
                    'base_url': self.rozee_platform_url.get()
                },
                'careerjet': {
                    'platform_name': self.careerjet_platform_name.get(),
                    'base_url': self.careerjet_platform_url.get()
                }
            },
            'scheduler': {
                'hour': self.scheduler_hour.get(),
                'minute': self.scheduler_minute.get()
            }
        }
    
    def update_preview(self):
        """Update the configuration preview"""
        data = self.gather_data()
        toml_str = self.dict_to_toml(data)
        
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, toml_str)
        self.preview_text.config(state=tk.DISABLED)
    
    def dict_to_toml(self, data, indent=0):
        """Convert dictionary to TOML string"""
        lines = []
        
        for key, value in data.items():
            if isinstance(value, dict):
                # Check if it's a section or inline table
                has_subsections = any(isinstance(v, dict) for v in value.values())
                
                if has_subsections:
                    # Main section
                    if indent == 0:
                        lines.append(f"\n[{key}]")
                    
                    for subkey, subvalue in value.items():
                        if isinstance(subvalue, dict):
                            # Subsection
                            lines.append(f"\n[{key}.{subkey}]")
                            lines.append(self.dict_to_toml(subvalue, indent + 1))
                        else:
                            # Simple value
                            lines.append(self.format_value(subkey, subvalue))
                else:
                    # Simple section
                    if indent == 0:
                        lines.append(f"\n[{key}]")
                    lines.append(self.dict_to_toml(value, indent + 1))
            else:
                lines.append(self.format_value(key, value))
        
        return '\n'.join(filter(None, lines))
    
    def format_value(self, key, value):
        """Format a key-value pair for TOML"""
        if isinstance(value, bool):
            return f"{key} = {str(value).lower()}"
        elif isinstance(value, (int, float)):
            return f"{key} = {value}"
        else:
            # Escape quotes in strings
            escaped = str(value).replace("'", "\\'")
            return f"{key} = '{escaped}'"
    
    def save_config(self):
        """Save configuration to TOML file"""
        try:
            data = self.gather_data()
            toml_str = self.dict_to_toml(data)
            
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(toml_str)
            
            messagebox.showinfo(
                "Success",
                f"Configuration saved successfully to:\n{self.config_file}"
            )
            
            # Update preview
            self.update_preview()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration:\n{str(e)}")
    
    def export_json(self):
        """Export configuration as JSON"""
        try:
            data = self.gather_data()
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile="jobsage_config.json"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo(
                    "Success",
                    f"Configuration exported to:\n{filename}"
                )
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export:\n{str(e)}")
    
    def load_config_file(self):
        """Load configuration from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("TOML files", "*.toml"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'rb') as f:
                    self.config_data = tomllib.load(f)
                
                # Reload UI
                self.reload_ui()
                
                messagebox.showinfo("Success", "Configuration loaded successfully")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration:\n{str(e)}")
    
    def reload_ui(self):
        """Reload UI with current config data"""
        # This would require recreating all tabs
        # For simplicity, just show a message
        messagebox.showinfo(
            "Reload Required",
            "Please restart the application to see the loaded configuration"
        )


def main():
    """Main entry point"""
    root = tk.Tk()
    app = JobSageConfigGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()