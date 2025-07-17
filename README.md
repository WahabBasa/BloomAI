# Active Recall Learning System

An AI-powered educational platform that transforms PDF documents into interactive learning experiences using active recall methodology.

**What it does:** Automatically generates practice questions from study materials and provides intelligent feedback to improve learning retention.

🔗 **Live Demo:** [Try it here](https://zealous-water-00b4c1200.6.azurestaticapps.net)

---

## How It Works

The system implements the active recall learning technique, where learners retrieve information from memory rather than passively reviewing content. This method has been proven to improve retention by up to 50%.

**User Flow:**
1. Upload a PDF study document
2. AI processes content and generates targeted questions
3. Complete practice sessions with instant feedback
4. Review detailed explanations and track progress

**Core Benefits:**
- Stronger memory formation through retrieval practice
- Immediate feedback with detailed explanations
- Personalized question generation from your materials
- Progress tracking to identify knowledge gaps

---

## System Architecture

```
┌─────────────┐    HTTP/JSON    ┌─────────────┐    Python     ┌─────────────┐
│   Vue.js    │ ────────────── │   Django    │ ──────────── │ AI Agents   │
│  Frontend   │                │   Backend   │              │ (OpenAI)    │
│             │                │             │              │             │
│ • UI/UX     │                │ • REST API  │              │ • PDF Extract│
│ • State     │                │ • Database  │              │ • Q Generator│
│ • Routing   │                │ • Business  │              │ • A Generator│
└─────────────┘                └─────────────┘              │ • Grader    │
                                                             └─────────────┘
```

**Technology Stack:**
- **Frontend:** Vue.js 3, Pinia, Vue Router
- **Backend:** Django, Django REST Framework
- **AI Framework:** Atomic Agents with OpenAI GPT-4
- **Database:** SQLite (development) / PostgreSQL (production)
- **Deployment:** Azure Web Apps + Azure Static Web Apps

---

## Features

### Core Functionality
- **PDF Processing:** Extract text content and metadata from educational documents
- **Intelligent Question Generation:** Create targeted active recall questions using AI
- **Automated Grading:** Evaluate responses with partial credit and detailed feedback
- **Progress Tracking:** Monitor learning performance across sessions
- **Responsive Design:** Works on desktop and mobile devices

### AI Capabilities
- Natural language understanding of educational content
- Context-aware question generation
- Nuanced answer evaluation beyond exact matching
- Detailed explanations that reinforce learning concepts

---

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone repository**
```bash
git clone <repository-url>
cd active-recall-system
```

2. **Backend setup**
```bash
cd Backend
pip install -r requirements.txt
echo "OPENAI_API_KEY=your_key_here" > .env
python manage.py migrate
python manage.py runserver
```

3. **Frontend setup** (new terminal)
```bash
cd Frontend
npm install
npm run dev
```

4. **Access application**
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`

---

## Backend Architecture

### Django Application Structure

```
Backend/
├── recall_system/          # Django project settings
├── main_system/            # Main application
│   ├── agents/            # AI agent implementations
│   ├── services/          # Business logic layer
│   ├── models.py          # Database models
│   ├── views.py           # API endpoints
│   └── tools/             # Utility tools
└── manage.py
```

### Database Models

```python
class Document(models.Model):
    document_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    content = models.TextField()  # Extracted text
    page_count = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Question(models.Model):
    question_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    question_text = models.TextField()
    answer_explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class UserAnswer(models.Model):
    answer_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_answer = models.TextField()
    mark = models.IntegerField()  # 0, 50, or 100
    submitted_at = models.DateTimeField(auto_now_add=True)
```

### API Endpoints

**Document Management:**
```http
POST   /api/documents/upload/              # Upload and process PDF
GET    /api/documents/                     # List all documents
GET    /api/documents/{id}/                # Get document details
```

**Question & Answer Flow:**
```http
GET    /api/documents/{id}/questions/      # Get questions for document
GET    /api/questions/{id}/                # Get specific question
POST   /api/questions/{id}/answer/         # Submit answer
GET    /api/answers/{id}/                  # Get graded answer
```

### Service Layer

The `recall_service.py` orchestrates the AI agent workflow:

```python
def process_pdf(document_id):
    """Complete PDF processing pipeline"""
    # 1. Extract content using PDFExtractorTool
    # 2. Generate questions using QuestionGenerator
    # 3. Create explanations using AnswerGenerator
    # 4. Store everything in database
    
def grade_answer(answer_id):
    """Evaluate user response"""
    # 1. Retrieve user answer and question context
    # 2. Use GradingAgent for evaluation
    # 3. Store grade and feedback
```

---

## AI Agents Implementation

### Atomic Agents Framework

The system uses four specialized AI agents built on the Atomic Agents framework, which provides:
- Structured input/output schemas with Pydantic
- Consistent prompt engineering patterns
- Easy integration with OpenAI models
- Type-safe agent interactions

### Agent Specifications

#### 1. PDF Extractor Tool
```python
class PDFExtractorTool(BaseTool):
    """Extracts text content and metadata from PDF files"""
    
    input_schema = PDFExtractorToolInputSchema
    output_schema = PDFExtractorToolOutputSchema
    
    # Uses PyPDF2 for text extraction
    # Handles metadata extraction (title, author, dates)
    # Returns structured content for further processing
```

#### 2. Question Generator Agent
```python
active_recall_agent = BaseAgent(
    model="gpt-4o-mini",
    system_prompt_generator=SystemPromptGenerator(
        background=[
            "Expert at generating effective active recall questions",
            "Focuses on key concepts and relationships",
            "Creates questions that promote deep learning"
        ],
        steps=[
            "Analyze content for key concepts",
            "Create targeted recall questions",
            "Format in markdown"
        ]
    )
)
```

#### 3. Answer Generator Agent
```python
answer_generator_agent = BaseAgent(
    model="gpt-4o-mini",
    system_prompt_generator=SystemPromptGenerator(
        background=[
            "Generates comprehensive explanations",
            "Provides correct answers with reasoning",
            "Reinforces conceptual understanding"
        ],
        output_instructions=[
            "Include both answer and reasoning",
            "Base explanations on source material",
            "Ensure educational value"
        ]
    )
)
```

#### 4. Grading Agent
```python
grading_agent = BaseAgent(
    model="gpt-4o-mini",
    system_prompt_generator=SystemPromptGenerator(
        background=[
            "Expert at evaluating learning responses",
            "Focuses on conceptual understanding",
            "Provides fair and objective assessment"
        ],
        output_instructions=[
            "Score: 0 (incorrect), 0.5 (partial), 1 (correct)",
            "Evaluate understanding, not exact wording",
            "Provide constructive feedback"
        ]
    )
)
```

---

## Frontend Architecture

### Vue.js Application Structure

```
Frontend/src/
├── components/          # Reusable UI components
│   ├── UploadForm.vue
│   ├── QuestionCard.vue
│   ├── NavigationButtons.vue
│   └── ResultItem.vue
├── views/              # Page-level components
│   ├── UploadView.vue
│   ├── TestView.vue
│   └── ResultsView.vue
├── stores/             # Pinia state management
│   └── testStore.js
├── services/           # API integration
│   └── apiService.js
└── router/
    └── index.js
```

### State Management with Pinia

```javascript
export const useTestStore = defineStore('test', {
  state: () => ({
    documentId: null,
    questions: [],
    currentQuestionIndex: 0,
    userAnswers: {},
    isTestCompleted: false
  }),
  
  getters: {
    currentQuestion: (state) => state.questions[state.currentQuestionIndex],
    totalQuestions: (state) => state.questions.length,
    results: (state) => /* computed results with grades */
  },
  
  actions: {
    async loadQuestions(documentId) { /* fetch from API */ },
    async submitAnswer(questionId, answer) { /* submit and grade */ },
    nextQuestion() { /* navigation logic */ }
  }
})
```

### API Service Layer

```javascript
const apiService = {
  async uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);
    return await fetch(`${API_BASE_URL}/documents/upload/`, {
      method: 'POST',
      body: formData
    });
  },
  
  async getQuestions(documentId) {
    return await fetch(`${API_BASE_URL}/documents/${documentId}/questions/`);
  },
  
  async submitAnswer(questionId, answer) {
    return await fetch(`${API_BASE_URL}/questions/${questionId}/answer/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answer })
    });
  }
}
```

---

## Azure Deployment Architecture

### Production Infrastructure

**Backend (Azure Web Apps):**
- **Service:** Azure App Service (Linux, Python 3.8)
- **URL:** `bloomai-hackathon-prd-wa-uaen-01-eaezdxhbegfvhgd7.uaenorth-01.azurewebsites.net`
- **Database:** SQLite (can be upgraded to Azure Database for PostgreSQL)
- **Environment Variables:** Configured in Azure App Service settings

**Frontend (Azure Static Web Apps):**
- **Service:** Azure Static Web Apps
- **URL:** `zealous-water-00b4c1200.6.azurestaticapps.net`
- **Build:** Automatic deployment from GitHub repository
- **CDN:** Global content delivery for optimal performance

**Cross-Origin Configuration:**
```python
# Django settings
CORS_ALLOWED_ORIGINS = [
    "https://zealous-water-00b4c1200.6.azurestaticapps.net"
]
```

### Environment Configuration

**Production Environment Variables:**
```bash
OPENAI_API_KEY=sk-...
DJANGO_SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=bloomai-hackathon-prd-wa-uaen-01-eaezdxhbegfvhgd7.uaenorth-01.azurewebsites.net
```

---

## Development Workflow

### Setting Up Development Environment

1. **Backend Development:**
```bash
cd Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

2. **Frontend Development:**
```bash
cd Frontend
npm install
npm run dev
```

3. **Environment Variables:**
Create `Backend/.env`:
```
OPENAI_API_KEY=your_openai_api_key
DJANGO_SECRET_KEY=your_django_secret_key
DEBUG=True
```

### Testing the System

1. **Upload a PDF:** Use the frontend to upload a test document
2. **Verify Processing:** Check Django admin or database for extracted content
3. **Test Questions:** Ensure questions are generated and stored correctly
4. **Test Grading:** Submit answers and verify grading logic
5. **Check Results:** Confirm proper display of scores and explanations

---

## Configuration Options

### AI Model Configuration

**Switching OpenAI Models:**
```python
# In agent configurations
model="gpt-4o-mini"  # Fast, cost-effective
model="gpt-4"        # Higher quality, more expensive
model="gpt-3.5-turbo"  # Balanced option
```

**Adjusting Question Count:**
```python
# In qgen_agent.py
question_count: Optional[int] = Field(5, description="Number of questions")
```

### Database Configuration

**Development (SQLite):**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Production (PostgreSQL):**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'your_db_host',
        'PORT': '5432',
    }
}
```

---

## Key Dependencies

### Backend Dependencies
```
Django==5.2
openai==1.x.x
instructor==0.x.x
atomic-agents==x.x.x
PyPDF2==3.x.x
django-cors-headers==4.x.x
python-dotenv==1.x.x
pydantic==2.x.x
```

### Frontend Dependencies
```
vue@3.5.13
pinia@3.0.1
vue-router@4.5.0
vite@6.2.4
```

---

## Educational Methodology

### Active Recall Principles

The system implements evidence-based learning techniques:

**Retrieval Practice:** Forces users to recall information from memory, strengthening neural pathways more effectively than passive review.

**Immediate Feedback:** Provides instant grading and explanations, crucial for correcting misconceptions and reinforcing correct understanding.

**Spaced Repetition Ready:** The grading system supports future implementation of spaced repetition algorithms where items are reviewed at increasing intervals.

**Metacognitive Awareness:** Detailed explanations help learners understand not just what the correct answer is, but why it's correct.

---

## Future Enhancement Opportunities

### Technical Improvements
- **Advanced PDF Processing:** Support for images, tables, and complex layouts
- **Multiple File Formats:** Word documents, PowerPoint, web articles
- **Real-time Collaboration:** Multi-user study sessions
- **Mobile Apps:** Native iOS/Android applications

### AI Enhancements
- **Adaptive Difficulty:** Questions that adjust to user performance
- **Learning Path Optimization:** AI-driven study recommendations
- **Multi-modal Content:** Questions incorporating images and diagrams
- **Personalized Explanations:** Tailored to individual learning styles

### Educational Features
- **Spaced Repetition:** Intelligent review scheduling
- **Progress Analytics:** Detailed learning insights and trends
- **Study Groups:** Collaborative learning features
- **Gamification:** Achievement systems and learning streaks

---

This system demonstrates a practical application of AI in education, combining modern web technologies with proven learning science to create an effective study tool. The modular architecture makes it easy to extend and customize for different educational contexts.
