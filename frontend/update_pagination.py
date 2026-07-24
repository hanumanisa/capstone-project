import re
import os

files = [
    "c:/xampp/htdocs/capstone-project/frontend/src/pages/CoursePage.jsx",
    "c:/xampp/htdocs/capstone-project/frontend/src/pages/EmployeePage.jsx",
    "c:/xampp/htdocs/capstone-project/frontend/src/pages/HotelPage.jsx",
    "c:/xampp/htdocs/capstone-project/frontend/src/pages/TnaPage.jsx",
    "c:/xampp/htdocs/capstone-project/frontend/src/pages/TrainingEvaluationEmployeePage.jsx",
    "c:/xampp/htdocs/capstone-project/frontend/src/pages/TrainingEvaluationPage.jsx",
    "c:/xampp/htdocs/capstone-project/frontend/src/pages/VendorPage.jsx"
]

for filepath in files:
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (not found)")
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Replace itemsPerPage = 20
    content = re.sub(r'const itemsPerPage\s*=\s*20;', 'const itemsPerPage = 50;', content)
    
    # 2. For TrainingEvaluationEmployeePage
    content = re.sub(
        r'\{\s*filteredCards\.length\s*>\s*0\s*&&\s*\(\s*(<div className="sticky bottom-0 bg-\[#F4F7FA\]/95 backdrop-blur-sm py-4 flex flex-col items-end gap-2 z-20 mt-4 border-t border-gray-100">.*?</div>\s*)\)\s*\}',
        r'\1',
        content,
        flags=re.DOTALL
    )

    # For TrainingEvaluationPage
    content = re.sub(
        r'\{\s*!loading\s*&&\s*filteredCards\.length\s*>\s*0\s*&&\s*\(\s*(<div className="sticky bottom-0 bg-\[#F4F7FA\]/95 backdrop-blur-sm py-4 flex flex-col items-end gap-2 z-20 mt-4 border-t border-gray-100">.*?</div>\s*)\)\s*\}',
        r'\1',
        content,
        flags=re.DOTALL
    )

    # For Vendor, Hotel, Employee, Course, Tna
    pattern = r'\{\s*(?:!loading\s*&&\s*\(\s*)?totalPages\s*>\s*1\s*\?\s*\(\s*(<div className="sticky bottom-0 bg-\[#F4F7FA\]/95 backdrop-blur-sm py-4 flex flex-col items-end gap-2 z-20 mt-4 border-t border-gray-100">.*?</div>\s*)\)\s*:\s*\(\s*(?:[\w\.]+\s*>\s*0\s*&&\s*\()?.*?Showing 1–.*?(?:\)\s*)?\)\s*(?:\)\s*)?\}'
    
    content = re.sub(
        pattern,
        r'\1',
        content,
        flags=re.DOTALL
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated {filepath}")
