"""
================================================================================
UTILS PACKAGE - Utility Functions
================================================================================
Package ini berisi modul-modul utilitas untuk aplikasi Logbook:
- formatters: Fungsi pemformatan data
- calculations: Fungsi perhitungan dan analisis
- validators: Fungsi validasi input
================================================================================
"""

from utils.formatters import (
    format_duration,
    format_duration_long,
    format_date,
    format_percentage,
    format_number,
    format_elapsed_time,
    truncate_text
)

from utils.calculations import (
    calculate_efficiency,
    get_efficiency_level,
    get_efficiency_color,
    get_efficiency_label,
    calculate_duration,
    calculate_progress,
    calculate_statistics,
    calculate_trend,
    calculate_average_per_day
)

from utils.validators import (
    validate_project_name,
    validate_estimated_hours,
    validate_category,
    validate_status,
    validate_time_range,
    validate_notes,
    validate_project,
    validate_activity,
    sanitize_string
)

__all__ = [
    # Formatters
    'format_duration',
    'format_duration_long',
    'format_date',
    'format_percentage',
    'format_number',
    'format_elapsed_time',
    'truncate_text',
    
    # Calculations
    'calculate_efficiency',
    'get_efficiency_level',
    'get_efficiency_color',
    'get_efficiency_label',
    'calculate_duration',
    'calculate_progress',
    'calculate_statistics',
    'calculate_trend',
    'calculate_average_per_day',
    
    # Validators
    'validate_project_name',
    'validate_estimated_hours',
    'validate_category',
    'validate_status',
    'validate_time_range',
    'validate_notes',
    'validate_project',
    'validate_activity',
    'sanitize_string'
]
