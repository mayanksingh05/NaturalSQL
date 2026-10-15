import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.interview_data import CATEGORIES

with open('INTERVIEW_PREP.md', 'w', encoding='utf-8') as f:
    f.write('# 🎯 NaturalSQL: 101 Technical & Architectural Interview Questions\n\n')
    f.write('> **Complete technical interview handbook for NaturalSQL covering core definitions, system architecture, SQL engineering, LLM integration, security, and cloud scalability.**\n\n---\n\n')
    
    q_count = 1
    for cat in CATEGORIES:
        f.write(f'## {cat["title"]}\n\n')
        for q, a in cat['questions']:
            f.write(f'### Q{q_count}: {q}\n')
            f.write(f'**Answer:** {a}\n\n')
            q_count += 1
            
    f.write('---\n\n*Generated for NaturalSQL Technical Interview Preparation.*\n')

print(f'INTERVIEW_PREP.md generated successfully with {q_count - 1} questions!')
