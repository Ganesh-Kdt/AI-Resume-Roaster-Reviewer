
from utils import job_role_to_industry

def get_roast_prompt(resume_text, job_role, job_description=""):
   industry = job_role_to_industry.get(job_role)
   return f"""
   You will see images of a résumé.
Please act like a hiring manager in {industry}.
Based on this resume, what would make you more likely to invite me for an interview? What should I change, cut, or add to improve my chances? Be brutally honest but constructive.
I want my resume to pass ATS filters and still read well to human recruiters. Based on the below job description, can you help me optimize my resume content to include relevant keywords and phrases from the posting in a natural way?

RESUME ANALYSIS TASK:

1. **RESUME ROAST** (Be brutally honest and roast the resume, Make it humiliating and funny, Make it as a joke):
   - Identify weak, vague, or generic phrases
   - Flag missing quantifiable achievements
   - Point out formatting/structure issues
   - Note missing keywords relevant to {job_role}
   - Highlight any red flags or inconsistencies

2. **SPECIFIC IMPROVEMENTS**:
   - Rewrite all weak bullet points and skills in work experience section with stronger action verbs
   - Most importantly, add quantifiable metrics where possible
   - Make them more relevant to {job_role}
   - Suggest better keywords to include
   - Group or re-order skills logically (Programming | Data | Cloud …)  
   - Insert missing, job-relevant tools / technologies found in the JD  
   - Remove irrelevant or obsolete skills  
   - Output as a concise comma-separated list or short bullets.

3. **GENERAL ADVICE**:
   - 2-3 extremely specific tips and skills required for this resume
   - Suggestions for missing sections if any

{f"**JOB DESCRIPTION**: {job_description}" if job_description else "**JOB DESCRIPTION**: Not provided - analysis will be based on general {job_role} requirements"}

**RESUME TO ANALYZE**:
\"\"\"
{resume_text}
\"\"\"

**REQUIRED OUTPUT FORMAT**:
🔥 **RESUME ROAST**:
- [List specific issues found]

✅ **IMPROVED BULLET POINTS**:
- Copy-paste the full, exact bullet from the original résumé for each pair (no paraphrasing, no truncation, no ellipses). Use only bullets from the Work Experience section.
- Format strictly as:
  - **Before**: <exact original bullet>
  
    **After**: <rewritten bullet with strong action verb, clear metric, and impact>
- Provide 4–6 pairs.

💡 **GENERAL TIPS**:
- [Specific actionable advice]
- [Mention the skills required for the job]
- [Mention the names of the certifications that will be helpful for the job]

**IMPORTANT**: Make the bullet points performance and metric based similar to the Google's XYZ format. And make fun of the resume in Resume Roast section. Make it humiliating and funny.
Keep your response focused,  performance based, actionable, and professional.
"""
