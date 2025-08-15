# UNEMPLOYMENT ANALYSIS WITH PYTHON

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

sns.set(style="whitegrid")

# Step 1: Import Libraries
print("📂 Current Folder:", os.getcwd())
print("📄 Files:", os.listdir())

# Step 2: Load Dataset
# Loads the CSV file and handles errors if the file is missing or corrupt.
def load_data(csv_file):
    try:
        data = pd.read_csv(csv_file)  
    except FileNotFoundError:
        messagebox.showerror("Error", f"❌ File not found: {csv_file}")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"❌ Error loading file: {e}")
        return None
    return data

# Step 3: Clean & Rename Columns
# Renames columns, converts date, and handles missing values.
def clean_data(data):
    # Remove leading/trailing spaces from column names
    data.columns = [col.strip() for col in data.columns]
    # Rename columns to match expected names
    data = data.rename(columns={
        'Region': 'State',  # 'Region' in CSV is actually the state name
        'Estimated Unemployment Rate (%)': 'Estimated Unemployment Rate',
        'Estimated Labour Participation Rate (%)': 'Estimated Labour Participation Rate',
        'Area': 'Region'    # 'Area' in CSV is Rural/Urban, treat as 'Region'
    })
    expected_columns = [
        'State', 'Date', 'Frequency', 'Estimated Unemployment Rate',
        'Estimated Employed', 'Estimated Labour Participation Rate', 'Region'
    ]
    missing_cols = [col for col in expected_columns if col not in data.columns]
    if missing_cols:
        messagebox.showerror("Error", f"Missing columns in CSV: {', '.join(missing_cols)}")
        return None
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
    data = data.dropna(subset=['State', 'Date', 'Estimated Unemployment Rate'])
    data['Estimated Employed'] = data['Estimated Employed'].fillna(0)
    data['Estimated Labour Participation Rate'] = data['Estimated Labour Participation Rate'].fillna(data['Estimated Labour Participation Rate'].mean())
    return data

# Step 4: Summary Output
# Prints summary statistics, region counts, and sample rows.
def show_summary():
    if app_data is not None:
        summary = app_data.describe()
        messagebox.showinfo("Summary", str(summary))
    else:
        messagebox.showwarning("Warning", "No data loaded.")

# Step 5: Unemployment Rate Over Time by Region
def plot_unemployment_by_region():
    if app_data is not None:
        selected_region = region_var.get()
        filtered = app_data if selected_region == "All" else app_data[app_data['Region'] == selected_region]
        fig, ax = plt.subplots(figsize=(12,6))
        sns.lineplot(data=filtered, x='Date', y='Estimated Unemployment Rate', hue='Region', marker='o', palette='tab10', ax=ax)
        ax.set_title(f'Unemployment Rate Over Time by Region: {selected_region}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Unemployment Rate (%)', fontsize=12)
        ax.legend(title='Region', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True)
        fig.tight_layout()
        show_plot_in_gui(fig)
    else:
        messagebox.showwarning("Warning", "No data loaded.")

# Step 6: Latest Unemployment Rate by State
def plot_latest_unemployment_by_state():
    if app_data is not None:
        selected_state = state_var.get()
        latest = app_data[app_data['Date'] == app_data['Date'].max()]
        filtered = latest if selected_state == "All" else latest[latest['State'] == selected_state]
        fig, ax = plt.subplots(figsize=(12,6))
        sns.barplot(
            data=filtered.sort_values(by='Estimated Unemployment Rate'),
            x='Estimated Unemployment Rate', y='State', palette='viridis', ax=ax
        )
        ax.set_title(f'Latest Unemployment Rate by State: {selected_state}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Unemployment Rate (%)', fontsize=12)
        ax.set_ylabel('State', fontsize=12)
        ax.grid(True, axis='x')
        fig.tight_layout()
        for i, v in enumerate(filtered.sort_values(by='Estimated Unemployment Rate')['Estimated Unemployment Rate']):
            ax.text(v + 0.2, i, f"{v:.1f}", color='black', va='center')
        show_plot_in_gui(fig)
    else:
        messagebox.showwarning("Warning", "No data loaded.")

# Step 7: Monthly Unemployment Rate Heatmap (Clearer View)
def plot_monthly_unemployment_heatmap():
    if app_data is not None:
        monthly = app_data.copy()
        monthly['Month'] = monthly['Date'].dt.to_period('M')
        pivot = monthly.pivot_table(index='State', columns='Month', values='Estimated Unemployment Rate')
        fig, ax = plt.subplots(figsize=(18,10))
        sns.heatmap(pivot, cmap='coolwarm', annot=True, fmt=".1f", linewidths=0.5, linecolor='gray', cbar_kws={'label': 'Unemployment Rate (%)'}, ax=ax)
        ax.set_title('📅 Monthly Unemployment Rate by State (Annotated)', fontsize=16, fontweight='bold')
        ax.set_xlabel('Month')
        ax.set_ylabel('State')
        fig.tight_layout()
        show_plot_in_gui(fig)
    else:
        messagebox.showwarning("Warning", "No data loaded.")

# Step 8: Correlation Matrix (Easily Readable)
def plot_correlation_matrix():
    if app_data is not None:
        correlation_data = app_data[['Estimated Unemployment Rate', 'Estimated Employed', 
                                    'Estimated Labour Participation Rate']].corr()
        fig, ax = plt.subplots(figsize=(7,5))
        sns.heatmap(correlation_data, annot=True, cmap='BrBG', fmt=".2f", linewidths=0.5, linecolor='gray', cbar_kws={'label': 'Correlation Coefficient'}, ax=ax)
        ax.set_title('📊 Correlation Matrix of Employment Metrics', fontsize=14, fontweight='bold')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
        fig.tight_layout()
        show_plot_in_gui(fig)
    else:
        messagebox.showwarning("Warning", "No data loaded.")

def export_summary():
    if app_data is not None:
        summary = app_data.describe()
        export_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if export_path:
            summary.to_csv(export_path)
            messagebox.showinfo("Export", f"Summary exported to {export_path}")
    else:
        messagebox.showwarning("Warning", "No data loaded.")

def open_file():
    global app_data
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        data = load_data(file_path)
        if data is not None:
            cleaned = clean_data(data)
            if cleaned is not None:
                app_data = cleaned
                update_dropdowns()
                messagebox.showinfo("Info", "Data loaded and cleaned successfully.")
            else:
                app_data = None

def show_help():
    help_text = (
        "Unemployment Analysis GUI\n\n"
        "1. Data is loaded automatically from 'Unemployment in India.csv'.\n"
        "2. Use the dropdowns to filter by region or state.\n"
        "3. Click buttons to view summary statistics and plots.\n"
        "4. Export summary statistics to CSV using the export button.\n"
        "5. For best results, ensure your CSV file has the correct columns.\n"
        "6. If you want to load a different file, use the Open CSV button.\n"
    )
    messagebox.showinfo("Help / About", help_text)

def update_dropdowns():
    # Update region and state dropdowns if new data is loaded
    region_options = ["All"] + sorted(app_data['Region'].unique()) if app_data is not None else ["All"]
    state_options = ["All"] + sorted(app_data['State'].unique()) if app_data is not None else ["All"]
    region_var.set("All")
    state_var.set("All")
    region_menu['menu'].delete(0, 'end')
    state_menu['menu'].delete(0, 'end')
    for option in region_options:
        region_menu['menu'].add_command(label=option, command=tk._setit(region_var, option))
    for option in state_options:
        state_menu['menu'].add_command(label=option, command=tk._setit(state_var, option))

app_data = None

# Automatically load CSV file on startup
csv_file = "Unemployment in India.csv"
if os.path.exists(csv_file):
    data = load_data(csv_file)
    if data is not None:
        cleaned = clean_data(data)
        if cleaned is not None:
            app_data = cleaned
        else:
            app_data = None
else:
    messagebox.showerror("Error", f"❌ File not found: {csv_file}")
    app_data = None

root = tk.Tk()
root.title("Unemployment Analysis GUI")

# Frame for filters
filter_frame = tk.Frame(root)
filter_frame.pack(pady=10)

tk.Label(filter_frame, text="Select Region:").grid(row=0, column=0, padx=5, pady=2)
region_options = ["All"] + sorted(app_data['Region'].unique()) if app_data is not None else ["All"]
region_var = tk.StringVar(value="All")
region_menu = tk.OptionMenu(filter_frame, region_var, *region_options)
region_menu.grid(row=0, column=1, padx=5, pady=2)

tk.Label(filter_frame, text="Select State:").grid(row=1, column=0, padx=5, pady=2)
state_options = ["All"] + sorted(app_data['State'].unique()) if app_data is not None else ["All"]
state_var = tk.StringVar(value="All")
state_menu = tk.OptionMenu(filter_frame, state_var, *state_options)
state_menu.grid(row=1, column=1, padx=5, pady=2)

# Frame for action buttons
action_frame = tk.Frame(root)
action_frame.pack(pady=10)

tk.Button(action_frame, text="Open CSV File", command=open_file).grid(row=0, column=0, padx=5, pady=2)
tk.Button(action_frame, text="Show Summary", command=show_summary).grid(row=0, column=1, padx=5, pady=2)
tk.Button(action_frame, text="Plot Unemployment by Region", command=plot_unemployment_by_region).grid(row=1, column=0, padx=5, pady=2)
tk.Button(action_frame, text="Plot Latest Unemployment by State", command=plot_latest_unemployment_by_state).grid(row=1, column=1, padx=5, pady=2)
tk.Button(action_frame, text="Plot Monthly Heatmap", command=plot_monthly_unemployment_heatmap).grid(row=2, column=0, padx=5, pady=2)
tk.Button(action_frame, text="Plot Correlation Matrix", command=plot_correlation_matrix).grid(row=2, column=1, padx=5, pady=2)
tk.Button(action_frame, text="Export Summary to CSV", command=export_summary).grid(row=3, column=0, padx=5, pady=2)
tk.Button(action_frame, text="Help / About", command=show_help).grid(row=3, column=1, padx=5, pady=2)

def show_plot_in_gui(fig):
    plot_window = tk.Toplevel(root)
    plot_window.title("Plot")
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

root.mainloop()


