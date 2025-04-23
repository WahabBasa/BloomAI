import os
from dotenv import load_dotenv
from rich.console import Console
import tkinter as tk
from tkinter import filedialog

# Load environment variables first
load_dotenv()

# Check if the API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("ERROR: OPENAI_API_KEY not found in environment variables!")
    print("Please make sure your .env file contains the OPENAI_API_KEY variable.")
    exit(1)
else:
    print("API key loaded successfully.")

from active_recall_system.tools.content_extractor import (
    PDFExtractorTool,
    PDFExtractorToolConfig,
    PDFExtractorToolInputSchema,
)

from active_recall_system.agents.qgen_agent import (
    ActiveRecallQuestionInputSchema, 
    active_recall_agent, 
    pdf_content_provider
)

# Import our answer generator agent
from active_recall_system.agents.agen_agent import (
    AnswerGeneratorInputSchema,
    answer_generator_agent,
    content_provider
)

# Import our grading agent
from active_recall_system.agents.g_agent import (
    GradingInputSchema,
    grading_agent,
    grading_context_provider
)

# Import our simplified question model
from active_recall_system.models.question_item import QuestionItem, QuestionStore

# Initialize a Rich Console for pretty console outputs
console = Console()

# Initialize the PDFExtractorTool
pdf_tool = PDFExtractorTool(config=PDFExtractorToolConfig())

# Initialize our QuestionStore
question_store = QuestionStore()

# Create simple file selector
def get_pdf_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(
        title="Select a PDF document",
        filetypes=[("PDF files", "*.pdf")]
    )
    return file_path

# Ask user to select a PDF file
console.print("[bold blue]Please select a PDF document...[/bold blue]")
pdf_file_path = get_pdf_file()

if not pdf_file_path:
    console.print("[bold red]No file selected. Exiting.[/bold red]")
    exit()

console.print(f"[bold green]Processing:[/bold green] {pdf_file_path}")

try:
    # Extract content from the PDF
    pdf_input = PDFExtractorToolInputSchema(file_path=pdf_file_path)
    pdf_output = pdf_tool.run(pdf_input)
    
    console.print(f"[bold green]Extracted PDF content[/bold green]")
    console.print(f"[bold green]Page count:[/bold green] {pdf_output.metadata.num_pages}")
    
    # Update pdf_content_provider with the extracted PDF data
    pdf_content_provider.content = pdf_output.content
    pdf_content_provider.title = pdf_output.metadata.title or "Untitled Document"
    pdf_content_provider.page_count = pdf_output.metadata.num_pages

    # Run the content through the question generator agent
    question_input = ActiveRecallQuestionInputSchema(
        document_id=os.path.basename(pdf_file_path),
        question_count=5  # Generate 5 questions by default
    )
    agent_response = active_recall_agent.run(question_input)
    
    # Store generated questions in a list for later use
    question_texts = agent_response.questions
    
    # Generate explanations using the answer generator agent
    console.print("[bold blue]Generating answer explanations...[/bold blue]")
    
    # Update the content provider for the answer generator
    content_provider.document_content = pdf_output.content
    content_provider.questions = question_texts
    
    # Run the answer generator agent
    answer_input = AnswerGeneratorInputSchema(
        document_content=pdf_output.content,
        questions=question_texts,
        document_title=pdf_output.metadata.title or "Untitled Document"
    )
    answer_response = answer_generator_agent.run(answer_input)
    
    # Create question items with questions and explanations
    questions = []
    for question_text, explanation in zip(question_texts, answer_response.explanations):
        # Create question item
        question_item = QuestionItem(
            question_text=question_text,
            answer_explanation=explanation
        )
        questions.append(question_item)
    
    # Save all questions to storage
    if question_store.save_questions(questions):
        console.print(f"[bold green]Saved {len(questions)} questions successfully![/bold green]")
    else:
        console.print(f"[bold red]Failed to save some questions.[/bold red]")
        
    # Interactive question-answering session - first collect all answers
    console.print("\n[bold blue]Starting active recall session...[/bold blue]")
    console.print("Answer each question to the best of your ability.\n")
    
    for i, question in enumerate(questions, 1):
        # Display the question
        console.print(f"[bold cyan]Question {i}:[/bold cyan]")
        console.print(question.question_text)
        console.print()
        
        # Get user's answer
        user_answer = input("Your answer: ")
        
        # Update the question with the user's answer
        question.user_answer = user_answer
        question_store.update_user_answer(question.question_id, user_answer)
        
        console.print("\n" + "-" * 50 + "\n")
    
    # After all questions are answered, perform grading
    console.print("[bold blue]Grading your answers...[/bold blue]\n")
    
    for i, question in enumerate(questions, 1):
        console.print(f"[bold cyan]Question {i}:[/bold cyan]")
        console.print(question.question_text)
        console.print(f"[italic]Your answer:[/italic] {question.user_answer}")
        
        # Grade the user's answer
        grading_context_provider.question = question.question_text
        grading_context_provider.explanation = question.answer_explanation
        grading_context_provider.user_answer = question.user_answer
        
        grading_input = GradingInputSchema(
            question=question.question_text,
            explanation=question.answer_explanation,
            user_answer=question.user_answer
        )
        
        grading_output = grading_agent.run(grading_input)
        
        # Update the question with the score
        question.mark = int(grading_output.score * 100)  # Convert to 0, 50, or 100
        question_store.update_mark(question.question_id, question.mark)
        
        # Display the score
        console.print(grading_output.markdown_score)
        
        # Display the correct explanation
        console.print("[bold green]Correct explanation:[/bold green]")
        console.print(question.answer_explanation)
        console.print("\n" + "-" * 50 + "\n")
    
    console.print("[bold blue]Active recall session completed![/bold blue]")
    console.print("Your answers and scores have been saved.")
    
except Exception as e:
    console.print(f"[bold red]Error:[/bold red] {str(e)}")