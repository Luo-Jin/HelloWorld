"""
Visualize school statistics data graphically.
Creates comprehensive charts for academic performance, demographics, staffing, and engagement.
"""

import sys
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import School, SchoolStats


def create_school_profile(school_id: int, year: int = 2024, save_file: bool = False):
    """
    Create a comprehensive visual profile of a school's statistics.
    
    Args:
        school_id: The school ID to visualize
        year: The year of statistics to display (default: 2024)
        save_file: Whether to save the figure to a file (default: False, displays instead)
    """
    with app.app_context():
        school = School.query.get(school_id)
        stats = SchoolStats.query.filter_by(sch_id=school_id, year=year).first()
        
        if not school or not stats:
            print(f"No data found for school ID {school_id}, year {year}")
            return
        
        # Create figure with multiple subplots
        fig = plt.figure(figsize=(16, 12))
        fig.suptitle(f'{school.sch_name} - {year} Comprehensive Statistics Profile', 
                     fontsize=18, fontweight='bold', y=0.98)
        
        gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)
        
        # Color scheme
        colors_ethnic = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        colors_ncea = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12', '#9b59b6']
        
        # ===== ROW 1: Demographics & Academic Performance =====
        
        # Ethnic Distribution (pie chart) - TOP LEFT
        ax1 = fig.add_subplot(gs[0, 0])
        ethnic_labels = ['European', 'Asian', 'Maori', 'Pacific', 'Other']
        ethnic_data = [
            stats.ethnic_european_pct,
            stats.ethnic_asian_pct,
            stats.ethnic_maori_pct,
            stats.ethnic_pacific_pct,
            stats.ethnic_other_pct
        ]
        wedges, texts, autotexts = ax1.pie(ethnic_data, labels=ethnic_labels, autopct='%1.1f%%',
                                            colors=colors_ethnic, startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        ax1.set_title('Ethnic Distribution', fontsize=11, fontweight='bold')
        
        # Student Demographics (gender + total) - TOP MIDDLE
        ax2 = fig.add_subplot(gs[0, 1])
        # Student Demographics (gender + total) - TOP MIDDLE
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.axis('off')
        demo_text = f"""
Student Demographics:

Total Students: {stats.total_students:,}

Gender Distribution:
  Male: {stats.male_pct:.1f}%
  Female: {stats.female_pct:.1f}%

School Type: {school.sch_type}
Decile: {stats.decile_rating}
        """
        ax2.text(0.05, 0.95, demo_text, transform=ax2.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        # NCEA Pass Rates (horizontal bar chart) - TOP RIGHT
        ax3 = fig.add_subplot(gs[0, 2])
        if stats.ncea_level_1_pass_pct is not None:
            ncea_levels = ['Level 1', 'Level 2', 'Level 3', 'Univ. Entrance', 'Endorsements']
            ncea_rates = [
                stats.ncea_level_1_pass_pct or 0,
                stats.ncea_level_2_pass_pct or 0,
                stats.ncea_level_3_pass_pct or 0,
                stats.university_entrance_pct or 0,
                stats.ncea_endorsement_pct or 0
            ]
            bars = ax3.barh(ncea_levels, ncea_rates, color=colors_ncea)
            ax3.set_xlabel('Pass Rate (%)', fontsize=10)
            ax3.set_title('NCEA Achievement Rates', fontsize=11, fontweight='bold')
            ax3.set_xlim(0, 100)
            for i, (bar, rate) in enumerate(zip(bars, ncea_rates)):
                if rate > 0:
                    ax3.text(rate + 1, i, f'{rate:.1f}%', va='center', fontsize=9)
        else:
            ax3.text(0.5, 0.5, 'No NCEA Data\n(Primary School)', 
                    ha='center', va='center', transform=ax3.transAxes, fontsize=11)
            ax3.set_title('NCEA Achievement Rates', fontsize=11, fontweight='bold')
            ax3.axis('off')
        # ===== ROW 2: Staffing & Resources =====
        
        # Staffing metrics (gauge-style bars)
        ax4 = fig.add_subplot(gs[1, 0])
        staffing_metrics = ['Student-Teacher\nRatio', 'Teachers\n(FTE)', 'Support Staff\n(FTE)']
        staffing_values = [
            stats.student_teacher_ratio or 15,
            stats.total_teachers_fte or 30,
            stats.support_staff_fte or 8
        ]
        staffing_max = [25, max(staffing_values[1], 50), max(staffing_values[2], 20)]
        
        x_pos = np.arange(len(staffing_metrics))
        bars = ax4.bar(x_pos, staffing_values, color=['#3498db', '#2ecc71', '#e74c3c'])
        ax4.set_ylabel('Count/Ratio', fontsize=10)
        ax4.set_title('Staffing & Resources', fontsize=11, fontweight='bold')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(staffing_metrics, fontsize=9)
        
        for i, (bar, val) in enumerate(zip(bars, staffing_values)):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{val:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Funding per student
        ax5 = fig.add_subplot(gs[1, 1])
        funding = stats.funding_per_student or 5000
        ax5.text(0.5, 0.7, f'${funding:,.0f}', ha='center', va='center',
                transform=ax5.transAxes, fontsize=32, fontweight='bold', color='#27ae60')
        ax5.text(0.5, 0.3, 'Funding per Student', ha='center', va='center',
                transform=ax5.transAxes, fontsize=12)
        ax5.axis('off')
        ax5.set_facecolor('#f0f0f0')
        
        # School Performance Rating
        ax6 = fig.add_subplot(gs[1, 2])
        ax6.axis('off')
        
        rating = stats.school_performance_rating or 'Good'
        rating_colors = {
            'Excellent': '#27ae60',
            'Good': '#3498db',
            'Improving': '#f39c12',
            'Requires Support': '#e74c3c'
        }
        rating_color = rating_colors.get(rating, '#95a5a6')
        
        performance_text = f"""
School Performance:

Rating: {rating}

Decile: {stats.decile_rating}/10
        """
        ax6.text(0.5, 0.5, rating, ha='center', va='center',
                transform=ax6.transAxes, fontsize=28, fontweight='bold',
                color=rating_color)
        ax6.text(0.5, 0.15, f"Decile {stats.decile_rating}", ha='center', va='center',
                transform=ax6.transAxes, fontsize=12)
        ax6.set_facecolor('#f8f8f8')
        
        # ===== ROW 3: Student Engagement =====
        
        # Engagement metrics (radar-like or bars)
        ax7 = fig.add_subplot(gs[2, :2])
        engagement_labels = ['Attendance', 'Retention', 'Suspension↓', 'Expulsion↓']
        # Note: suspension and expulsion are inverted so higher is better (100% - rate)
        engagement_values = [
            stats.attendance_rate_pct or 90,
            stats.student_retention_pct or 95,
            100 - (stats.suspension_rate_pct or 2),  # Inverted: lower suspension is better
            100 - (stats.expulsion_rate_pct or 0.1) * 100  # Inverted: lower expulsion is better
        ]
        engagement_value_actual = [
            stats.attendance_rate_pct or 90,
            stats.student_retention_pct or 95,
            stats.suspension_rate_pct or 2,
            stats.expulsion_rate_pct or 0.1
        ]
        
        x_pos = np.arange(len(engagement_labels))
        colors_engage = ['#2ecc71', '#2ecc71', '#3498db', '#3498db']
        bars = ax7.bar(x_pos, engagement_values, color=colors_engage)
        
        ax7.set_ylabel('Score (%)', fontsize=10)
        ax7.set_title('Student Engagement & Wellbeing', fontsize=11, fontweight='bold')
        ax7.set_xticks(x_pos)
        ax7.set_xticklabels(engagement_labels, fontsize=10)
        ax7.set_ylim(0, 105)
        ax7.axhline(y=90, color='gray', linestyle='--', linewidth=1, alpha=0.5)
        
        # Add value labels
        for i, (bar, label, val) in enumerate(zip(bars, engagement_labels, engagement_value_actual)):
            if 'Suspension' in label:
                label_text = f'{val:.1f}%'
            elif 'Expulsion' in label:
                label_text = f'{val:.2f}%'
            else:
                label_text = f'{val:.1f}%'
            
            height = bar.get_height()
            ax7.text(bar.get_x() + bar.get_width()/2., height + 1,
                    label_text, ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Data Source & Metadata
        ax8 = fig.add_subplot(gs[2, 2])
        ax8.axis('off')
        metadata_text = f"""
Data Source:
{stats.data_source}

Year: {year}

Updated:
{stats.last_updated.strftime('%Y-%m-%d %H:%M')}
        """
        ax8.text(0.05, 0.95, metadata_text, transform=ax8.transAxes, fontsize=9,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
        
        # Display or save
        if save_file:
            filename = f"school_{school_id}_{year}_profile.png"
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"✓ Saved visualization to {filename}")
        else:
            plt.tight_layout()
            plt.show()


def compare_schools(school_ids: list, year: int = 2024, metric: str = 'attendance'):
    """
    Compare multiple schools on a specific metric.
    
    Args:
        school_ids: List of school IDs to compare
        year: The year of statistics to compare
        metric: The metric to compare ('attendance', 'ncea_l3', 'str', 'funding', etc.)
    """
    with app.app_context():
        schools_data = []
        metric_values = []
        
        for school_id in school_ids:
            school = School.query.get(school_id)
            stats = SchoolStats.query.filter_by(sch_id=school_id, year=year).first()
            
            if school and stats:
                schools_data.append((school.sch_name, stats))
                
                # Get metric value
                if metric == 'attendance':
                    value = stats.attendance_rate_pct
                elif metric == 'ncea_l3':
                    value = stats.ncea_level_3_pass_pct
                elif metric == 'str':
                    value = stats.student_teacher_ratio
                elif metric == 'funding':
                    value = stats.funding_per_student / 1000  # in thousands
                elif metric == 'suspension':
                    value = stats.suspension_rate_pct
                else:
                    value = stats.attendance_rate_pct
                
                metric_values.append(value if value else 0)
        
        if not schools_data:
            print("No data found for comparison")
            return
        
        # Create comparison chart
        fig, ax = plt.subplots(figsize=(12, 6))
        
        school_names = [name for name, _ in schools_data]
        x_pos = np.arange(len(school_names))
        
        colors_comp = plt.cm.Set3(np.linspace(0, 1, len(school_names)))
        bars = ax.bar(x_pos, metric_values, color=colors_comp)
        
        ax.set_ylabel(f'{metric.replace("_", " ").title()} Value', fontsize=11)
        ax.set_title(f'School Comparison - {metric.replace("_", " ").title()} ({year})', 
                    fontsize=13, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(school_names, rotation=45, ha='right')
        
        # Add value labels
        for bar, val in zip(bars, metric_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(metric_values) * 0.02,
                   f'{val:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        plt.show()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Visualize school statistics data')
    parser.add_argument('--school', type=int, required=True, help='School ID to visualize')
    parser.add_argument('--year', type=int, default=2024, help='Year of statistics (default: 2024)')
    parser.add_argument('--save', action='store_true', help='Save figure to file instead of displaying')
    parser.add_argument('--compare', type=int, nargs='+', help='Compare multiple schools (provide multiple school IDs)')
    parser.add_argument('--metric', default='attendance', help='Metric to compare: attendance, ncea_l3, str, funding, suspension')
    
    args = parser.parse_args()
    
    app = create_app()
    
    if args.compare:
        compare_schools(args.compare, args.year, args.metric)
    else:
        create_school_profile(args.school, args.year, args.save)
