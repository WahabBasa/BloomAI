# Active Recall Learning System

A specialized learning tool built with Atomic Agents that leverages active recall techniques to enhance knowledge retention and understanding.

## Overview

This system transforms educational content into interactive learning experiences through a series of specialized AI agents.

## How It Works

## PDF Extractor Tool

The system includes a powerful PDF content extraction tool that:

- Extracts text content from PDF documents with precision
- Supports selective page extraction (specific pages or entire documents)
- Retrieves comprehensive document metadata including title, author, creation date
- Provides document statistics such as total page count
- Returns structured output with organized content and metadata
- Handles potential errors with robust exception management
- Built using PyPDF2 for reliable document processing

This extraction capability forms the foundation of the learning system by transforming static PDF educational materials into processable content for question generation.

2. **Question Generator** transforms extracted text into targeted active recall questions
3. **Answer Generator** creates detailed explanations for each question
4. **Grading Agent** evaluates user responses against the explained answers

## Core Components

The system relies on a central `Test` class that maintains:

- Questions derived from source material
- Comprehensive answer explanations
- User-submitted responses
- Performance marks for each question

