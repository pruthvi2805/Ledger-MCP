import os
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any
from .db import DB

class ReportGenerator:
    def __init__(self):
        self.width = 0
        self.height = 0
    
    def generate_pdf(self, month: int, year: int, output_path: str = None) -> str:
        """
        Generate a professional PDF report for the given month/year.
        Returns the absolute path to the generated PDF.
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
        except ImportError:
            raise ImportError("Please run 'pip install reportlab matplotlib' to generic PDF reports.")

        # 1. Fetch Data
        start_date = f"{year}-{month:02d}-01"
        if month == 12: 
            end_date = f"{year+1}-01-01"
        else: 
            end_date = f"{year}-{month+1:02d}-01"

        with DB.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get Base Currency
            cursor.execute("SELECT value FROM config WHERE key='base_currency'")
            row = cursor.fetchone()
            base_currency = row['value'].decode('utf-8') if row and row['value'] else 'INR'
            
            # Summary by Category & Currency
            cursor.execute("""
                SELECT category, currency, SUM(amount) as total 
                FROM transactions 
                WHERE date >= ? AND date < ? 
                GROUP BY category, currency
            """, (start_date, end_date))
            cat_rows = cursor.fetchall()
            
            # Top Merchants
            cursor.execute("""
                SELECT merchant, SUM(amount) as total, currency
                FROM transactions
                WHERE date >= ? AND date < ? AND merchant IS NOT NULL
                GROUP BY merchant, currency
                ORDER BY total ASC -- Expenses are negative, most negative is top spender
                LIMIT 10
            """, (start_date, end_date))
            # Fix logic: "Total" is negative for spending. Order by total ASC gives biggest spenders.
            top_merchants = cursor.fetchall()
            
            # Daily Spending Trend
            cursor.execute("""
                SELECT date, SUM(amount) as total
                FROM transactions
                WHERE date >= ? AND date < ?
                GROUP BY date
                ORDER BY date
            """, (start_date, end_date))
            daily_rows = cursor.fetchall()

        # 2. Process Data
        summary = defaultdict(lambda: defaultdict(float))
        total_spent = defaultdict(float)
        
        for row in cat_rows:
            amt = row['total'] / 100.0
            curr = row['currency'] or 'INR'
            if amt < 0: # Only expenses for charts
                summary[row['category']][curr] += abs(amt)
                total_spent[curr] += abs(amt)

        # 3. Setup PDF
        if not output_path:
            # Save to user's Documents folder ideally, or current dir
            filename = f"Financial_Report_{year}_{month:02d}.pdf"
            output_path = os.path.abspath(filename)

        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph(f"Financial Report: {datetime(year, month, 1).strftime('%B %Y')}", styles['Title']))
        story.append(Spacer(1, 0.2*inch))

        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        
        # Calculate Grand Total using stored Normalized Amounts (accurate historical rates)
        with DB.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(amount_normalized) 
                FROM transactions 
                WHERE date >= ? AND date < ?
            """, (start_date, end_date))
            row = cursor.fetchone()
            grand_total = row[0] if row and row[0] else 0.0
        
        summary_text = []
        for curr, amt in total_spent.items():
            summary_text.append(f"• Total Spending ({curr}): {curr} {amt:,.2f}")
            
        summary_text.insert(0, f"<b>Grand Total ({base_currency}): {base_currency} {abs(grand_total):,.2f}</b>")
        summary_text.insert(1, "") # Spacer
        
        if not total_spent:
            story.append(Paragraph("No spending data found for this month.", styles['Normal']))
            doc.build(story)
            return output_path
            
        story.append(Paragraph("<br/>".join(summary_text), styles['Normal']))
        story.append(Spacer(1, 0.2*inch))

        # Charts Generation
        # Pie Chart (Top Categories in primary currency)
        primary_curr = base_currency
        
        pie_data = []
        pie_labels = []
        for cat, curr_map in summary.items():
            if primary_curr in curr_map:
                pie_data.append(curr_map[primary_curr])
                pie_labels.append(cat)
        
        # Limit to top 8 slices
        if len(pie_data) > 8:
            combined = sorted(zip(pie_data, pie_labels), reverse=True)
            pie_data = [x[0] for x in combined[:7]]
            pie_labels = [x[1] for x in combined[:7]]
            other_amt = sum([x[0] for x in combined[7:]])
            pie_data.append(other_amt)
            pie_labels.append("Others")
            
        if pie_data:
            plt.figure(figsize=(6, 4))
            plt.pie(pie_data, labels=pie_labels, autopct='%1.1f%%', startangle=90)
            plt.title(f"Spending by Category ({primary_curr})")
            chart_filename = f"temp_chart_{year}_{month}.png"
            plt.savefig(chart_filename)
            plt.close()
            
            story.append(Image(chart_filename, width=400, height=300))
            story.append(Spacer(1, 0.2*inch))

        # Top Merchants Table
        story.append(Paragraph("Top Spending Merchants", styles['Heading2']))
        table_data = [['Merchant', 'Currency', 'Amount']]
        for row in top_merchants:
            # Expenses are negative, but we want to show positive magnitude
            if row['total'] < 0:
                table_data.append([
                    row['merchant'] or "Unknown",
                    row['currency'] or 'INR',
                    f"{abs(row['total']/100.0):,.2f}"
                ])
        
        if len(table_data) > 1:
            t = Table(table_data, colWidths=[3*inch, 1*inch, 1.5*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
            ]))
            story.append(t)

        # Build PDF
        doc.build(story)
        
        # Cleanup
        if os.path.exists(f"temp_chart_{year}_{month}.png"):
            os.remove(f"temp_chart_{year}_{month}.png")
            
        return output_path
