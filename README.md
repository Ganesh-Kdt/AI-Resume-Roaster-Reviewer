# 🔥 AI Resume Roaster + Rewriter

An intelligent AI-powered application that analyzes resumes, provides brutally honest feedback, and automatically rewrites bullet points to improve your chances of landing interviews. Built with Streamlit and OpenAI's GPT models.

## ✨ Features

- **📄 PDF Resume Processing**: Upload and extract text from PDF resumes
- **🎯 Job-Specific Analysis**: Tailored feedback based on your target job role
- **🤖 AI-Powered Feedback**: Brutal but constructive resume roasting from AI hiring managers
- **✍️ Automatic Rewriting**: AI rewrites weak bullet points with strong action verbs and metrics
- **📊 ATS Score Calculation**: Get a numerical score to measure resume effectiveness
- **🔍 Vision Analysis**: Uses GPT-Vision to analyze resume formatting and layout
- **💾 Download Updated Resume**: Get your improved resume as a text file

## 🚀 How It Works

1. **Upload Your Resume**: Drop your PDF resume (max 10MB)
2. **Set Your Target**: Choose your job role and paste the job description
3. **AI Analysis**: Our AI acts as a hiring manager and roasts your resume
4. **Get Improvements**: Receive rewritten bullet points with metrics and impact
5. **Download Results**: Get your enhanced resume and ATS score

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI Models**: OpenAI GPT-4o (Vision)
- **Image Processing**: Pillow (PIL)

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Poppler (for PDF processing on some systems)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd AI-Resume-Roaster
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Streamlit secrets**
   Create `.streamlit/secrets.toml` with your OpenAI API key:
   ```toml
   OPENAI_API_KEY = "your-openai-api-key-here"
   ```

4. **Configure Streamlit settings**
   The app is already configured with:
   - 10MB file upload limit
   - Optimized client settings

## 🎯 Supported Job Roles

- Software Engineer
- Data Scientist
- Product Manager
- UX Designer
- Cybersecurity Analyst

## 📖 Usage

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **Upload your resume**
   - Supported format: PDF only
   - Maximum size: 10MB
   - The app will extract and display the text

3. **Configure your target**
   - Select your target job role
   - Paste the job description for targeted feedback

4. **Get AI feedback**
   - Click "Get Feedback from AI"
   - Wait for the AI analysis (may take a few moments)

5. **Review and download**
   - Read the brutal but helpful feedback
   - View your improved bullet points
   - Download the enhanced resume
   - Check your ATS score

## 🔧 Configuration

### File Size Limits
- **10MB upload limit** configured in `.streamlit/config.toml`
- Automatically enforced by Streamlit server

### AI Model Settings
- **Default Model**: GPT-4o (Vision)
- **Temperature**: 0.7 (balanced creativity and consistency)
- **Vision Analysis**: Enabled for better resume formatting analysis

## 📊 ATS Scoring System

The app calculates an ATS (Applicant Tracking System) score based on:

- **Keyword Match (50%)**: Relevance to job description
- **Section Coverage (15%)**: Presence of required sections
- **Impact Metrics (15%)**: Quantifiable achievements
- **Action Verbs (10%)**: Strong, dynamic language
- **Length Optimization (10%)**: Appropriate resume length

**Score Levels:**
- 90-100: Resume Legend 🏆
- 80-89: Resume Master 🥇
- 70-79: Resume Pro 🥈
- 60-69: Resume Builder 🥉
- 50-59: Resume Rookie 🌱
- <50: Resume Seedling 🌱

## 🎨 Customization

### Adding New Job Roles
Edit `utils.py` to add new roles to the `job_role_to_industry` dictionary:

```python
job_role_to_industry = {
    "Your New Role": "Your Industry Category",
    # ... existing roles
}
```

### Modifying Prompts
Edit `prompts.py` to customize the AI feedback style and requirements.

### Adjusting ATS Scoring
Modify the scoring functions in `utils.py` to change how resumes are evaluated.

## 🐛 Troubleshooting

### Common Issues

1. **"OpenAI API key not found"**
   - Ensure your API key is in `.streamlit/secrets.toml`
   - Check the key format and validity

2. **File upload errors**
   - Verify file is PDF format
   - Check file size is under 10MB
   - Ensure proper file permissions

3. **PDF processing issues**
   - Try re-uploading the PDF
   - Ensure PDF is not password-protected
   - Check if PDF contains extractable text

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Happy Resume Roasting! 🔥📄**

*Remember: The AI's brutal honesty is meant to help you improve. Take the feedback constructively and watch your resume transform from "meh" to "wow!"* 