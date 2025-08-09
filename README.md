# 🚀 Social Post Generator

> **AI-Powered Social Media Content Creation with Persistent Company Profiles**

Transform your business information int## 🚀 Deployment Options

### Local Development
```bash
streamlit run main.py
```

### Streamlit Cloud (Recommended)

1. **Fork/Clone** this repository to your GitHub
2. **Connect** to [Streamlit Cloud](https://streamlit.io/cloud)
3. **Deploy** your app from GitHub
4. **Add Secrets** in your app dashboard:

```toml
# In Streamlit Cloud → App Settings → Secrets
OPENAI_API_KEY = "your_openai_api_key_here"
APP_PASSWORD = "your_app_password_here"
```

### Other Production Deployments
- **Heroku**: Ready with `Procfile` and `app.json`
- **Docker**: Containerized deployment
- **Cloud Platforms**: Compatible with major cloud providerssocial media captions using advanced AI technology. Simply enter your website URL, upload reference images, and generate platform-optimized content that speaks directly to your target audience.

## ✨ Key Features

### � **Persistent Company Profiles**
- **Shared Database**: Company profiles persist across all users and sessions
- **Quick Load**: Save and reload business information instantly
- **Team Collaboration**: Multiple users can access the same company database
- **Auto-Population**: Website analysis automatically creates company profiles

### 🤖 **AI-Powered Caption Generation**
- **Dual AI Models**: Choose between GPT-4o-mini (cost-effective) or GPT-4o (premium quality)
- **Platform Optimization**: Generate content optimized for all social platforms
- **Length Options**: "All Social Platforms", "2-3 sentences", "3-4 sentences", or platform-specific
- **Smart Targeting**: AI considers your business type, audience, and product details
- **Call-to-Action**: Optional CTA integration (enabled by default)

### 🌐 **Intelligent Website Analysis**
- **Multi-Strategy Scraping**: Advanced error handling with multiple fallback methods
- **Business Intelligence**: Extracts company info, target audience, and value propositions
- **403 Error Mitigation**: User-agent rotation and session-based requests
- **Auto-Population**: Seamlessly fills business details from website content

### 📸 **Simple Image Upload**
- **Reference Images**: Upload single or multiple images for caption context
- **Format Support**: PNG, JPG, JPEG, WebP (up to 5MB each)
- **Visual Preview**: Thumbnail previews with drag-and-drop functionality
- **Batch Processing**: Handle multiple images simultaneously

### 🎨 **Clean User Interface**
- **Intuitive Workflow**: Streamlined single-page design
- **Start Over Button**: Always visible at top of sidebar
- **Collapsible Sections**: Keep interface clean and focused
- **Mobile Responsive**: Works perfectly on all device sizes
- **Professional Design**: No clutter, no popups, business-focused aesthetics

## 🛠️ Quick Setup

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/VanPete/Social-Post-Generator.git
   cd Social-Post-Generator
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create environment file** (for local development):
   ```bash
   # Create .env file with your secrets
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   echo "APP_PASSWORD=your_password_here" >> .env
   ```

4. **Run the application**:
   ```bash
   streamlit run main.py
   ```

### For Streamlit Cloud Deployment
The application automatically detects when running on Streamlit Cloud and uses the secrets manager instead of environment variables. No additional configuration needed!

## 🚀 How to Use

### 1. **Website Analysis** (Recommended Start)
- Enter your company website URL
- AI automatically extracts business information
- Company profile is created and saved permanently

### 2. **Business Details**
- Verify/edit extracted information
- Add product/service details
- Specify target audience

### 3. **Optional Image Upload**
- Upload reference images (products, services, branding)
- Images provide context for more targeted captions

### 4. **Generate Captions**
- Choose platform or length preference
- Call-to-action is enabled by default
- Generate 3 unique, engaging captions

### 5. **Save & Reuse**
- Company profiles automatically saved
- Quick reload for future sessions
- Shared across all users

## 📁 Project Structure

```
Social-Post-Generator/
├── main.py                     # Main application entry point
├── config/
│   ├── constants.py            # Platform settings, models, limits
│   └── settings.py             # Application configuration
├── modules/
│   ├── auth.py                 # Password authentication
│   ├── business_info.py        # Business information management
│   ├── caption_generator.py    # AI caption generation + triggers
│   ├── companies.py            # Persistent company profiles
│   ├── image_processing.py     # Simple image upload handling
│   ├── ui_components.py        # Platform selectors, UI elements
│   └── website_analysis.py     # Intelligent website scraping
├── utils/
│   ├── helpers.py              # Utility functions
│   └── file_ops.py             # JSON file operations
├── company_profiles.json       # Persistent company database
├── app_statistics.json         # Usage analytics
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔧 Configuration

### Platform Settings
The application supports multiple caption length options:

- **All Social Platforms (Default)**: Character fitting for universal use
- **2-3 sentences**: Short and engaging
- **3-4 sentences**: Medium length content
- **Twitter/X**: ≤280 characters
- **Instagram**: ≤2,200 characters  
- **LinkedIn**: ≤3,000 characters
- **Facebook**: Longer form content

### AI Models
- **GPT-4o-mini**: Cost-effective, fast, great for most use cases
- **GPT-4o**: Premium quality, more sophisticated output

## 🔐 Security Features

- **Password Protection**: Secure access with configurable password
- **Session Management**: Secure user sessions with proper logout
- **Environment Variables**: Sensitive data stored securely

## 📊 Analytics & Tracking

- **Usage Statistics**: Track caption generation metrics
- **Company Profiles**: Monitor saved profiles and usage patterns
- **Performance Insights**: Analyze application usage over time

## � Deployment Options

### Local Development
```bash
streamlit run main.py
```

### Production Deployment
- **Heroku**: Ready with `Procfile` and `app.json`
- **Docker**: Containerized deployment
- **Cloud Platforms**: Compatible with major cloud providers

## 🤝 Contributing

We welcome contributions! Areas for improvement:

- **UI/UX Enhancements**: Better responsive design
- **Additional Platforms**: TikTok, Pinterest, YouTube optimizations
- **Advanced Features**: A/B testing, analytics dashboard
- **Integrations**: Direct social media posting

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Documentation**: Comprehensive guides in the `/docs` folder
- **Community**: Join our discussions for tips and best practices

---

**Built with ❤️ using Streamlit, OpenAI, and modern Python practices**

*Transform your business communications with AI-powered social media content generation*

   ```bash
   streamlit run main.py
   ```

### Method 2: Using Batch File (Windows)

   ```bat
   run_social_generator.bat
   ```

### Method 3: Original Application (Legacy)

   ```bash
   streamlit run main.py
   ```

## 📋 How It Works

1. **📸 Upload Image**: Choose your social media photo
2. **🏢 Enter Business Info**: Type your business name or category
3. **🌐 Add Website (Optional)**: Provide company URL for brand-specific content
4. **⚡ Generate**: Get 3 professional, ready-to-post captions!

## 🎯 Example Usage

- **Restaurant**: Upload food photo + "Italian Restaurant" + olivegarden.com
- **Fitness**: Upload workout photo + "Fitness Studio" + orangetheory.com  
- **Tech**: Upload office photo + "Software Company" + microsoft.com

## 💡 Features & Benefits

| Feature | Benefit |
|---------|---------|
| Website Analysis | Brand-aligned, authentic captions |
| Dual AI Models | Balance quality vs cost |
| Smart Caching | Faster repeated website analysis |
| Download Captions | Easy copy-paste to social platforms |
| Error Handling | Graceful failure with helpful messages |

## 📁 Project Structure (v2.0 - Modular Architecture)

   ```text
   Social Post Generator/
   ├── 🚀 main.py                    # New modular entry point (Primary - Use this!)
   ├── 📜 social_post_generator.py   # Original monolithic file (DEPRECATED - Remove after migration)
   ├── 📁 config/                   # Application configuration
   │   ├── constants.py             # App constants and settings (52 lines)
   │   └── settings.py              # Data classes and configuration objects (28 lines)
   ├── 📁 modules/                  # Core business logic modules
   │   ├── auth.py                  # Authentication and session management (94 lines)
   │   ├── captions.py              # Caption tracking and analytics (312 lines)
   │   ├── companies.py             # Company profile management (298 lines)
   │   ├── website_analysis.py      # Website analysis engine (273 lines)
   │   ├── image_processing.py      # Image editing and batch processing (571 lines)
   │   └── templates.py             # Social media templates and analytics (557 lines)
   ├── 📁 utils/                    # Shared utilities
   │   ├── file_ops.py              # JSON file operations (71 lines)
   │   └── helpers.py               # Common utility functions (119 lines)
   ├── 📁 .venv/                    # Virtual environment
   ├── 🔐 .env                      # API keys (create this)
   ├── requirements.txt             # Dependencies
   ├── run_social_generator.bat     # Windows launcher
   └── README.md                    # This documentation

   🎯 Total Refactored Code: ~2,900 lines across 10 files
   📊 Code Reduction: ~40% while adding new features
   ✅ Maintainability: Significantly improved
   ```

## 🔧 Dependencies

- **streamlit**: Web UI framework
- **openai**: GPT-4 vision API
- **beautifulsoup4**: Website scraping
- **requests**: HTTP requests
- **Pillow**: Image processing
- **python-dotenv**: Environment variables

## 🛡️ Error Handling

The app handles:

- Missing API keys
- Invalid websites
- Network timeouts
- API quota limits
- Unsupported image formats

## 💰 Cost Management

- **GPT-4o-mini**: ~60% cheaper, great for testing
- **GPT-4o**: Premium quality for production use
- **Smart Caching**: Reduces repeated API calls

## 🎨 Customization

The Streamlit app is easily customizable:

- UI layout and styling
- Prompt engineering
- Website analysis rules
- Caption formatting

---

## Built with ❤️ for Maddie
