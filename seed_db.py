"""
Seed script to populate the database with initial data.
Run this script after creating the database to populate it with sample questions.
"""
from sqlalchemy.orm import Session
from database import get_db, engine, Base
import models

# Create tables
Base.metadata.create_all(bind=engine)

def seed_questions():
    """Seed the database with initial questions."""
    # Get db session
    db = next(get_db())
    
    try:
        # Check if we already have questions
        existing_count = db.query(models.Question).count()
        if existing_count > 0:
            print("Database already has questions. Skipping seeding.")
            return
        
        # Question 1: Full Name
        q1 = models.Question(
            name="full_name",
            type="short_text",
            required=True,
            text="What is your full name?",
            description="[Surname] [First Name] [Other Names]"
        )
        db.add(q1)
        
        # Question 2: Email Address
        q2 = models.Question(
            name="email_address",
            type="email",
            required=True,
            text="What is your email address?",
            description=""
        )
        db.add(q2)
        
        # Question 3: Description
        q3 = models.Question(
            name="description",
            type="long_text",
            required=True,
            text="Tell us a bit more about yourself",
            description=""
        )
        db.add(q3)
        
        # Question 4: Gender
        q4 = models.Question(
            name="gender",
            type="choice",
            required=True,
            text="What is your gender?",
            description="",
            multiple_choice=False
        )
        db.add(q4)
        
        # Flush to get q4 ID
        db.flush()
        
        # Add gender options
        gender_options = [
            models.QuestionOption(question_id=q4.id, value="MALE", text="Male"),
            models.QuestionOption(question_id=q4.id, value="FEMALE", text="Female"),
            models.QuestionOption(question_id=q4.id, value="OTHER", text="Other")
        ]
        db.add_all(gender_options)
        
        # Question 5: Programming Stack
        q5 = models.Question(
            name="programming_stack",
            type="choice",
            required=True,
            text="What programming stack are you familiar with?",
            description="You can select multiple",
            multiple_choice=True
        )
        db.add(q5)
        
        # Flush to get q5 ID
        db.flush()
        
        # Add programming stack options
        stack_options = [
            models.QuestionOption(question_id=q5.id, value="REACT", text="React JS"),
            models.QuestionOption(question_id=q5.id, value="ANGULAR", text="Angular JS"),
            models.QuestionOption(question_id=q5.id, value="VUE", text="Vue JS"),
            models.QuestionOption(question_id=q5.id, value="SVELTE", text="Svelte"),
            models.QuestionOption(question_id=q5.id, value="SQL", text="SQL"),
            models.QuestionOption(question_id=q5.id, value="POSTGRES", text="Postgres"),
            models.QuestionOption(question_id=q5.id, value="MYSQL", text="MySQL"),
            models.QuestionOption(question_id=q5.id, value="MSSQL", text="Microsoft SQL Server"),
            models.QuestionOption(question_id=q5.id, value="JAVA", text="Java"),
            models.QuestionOption(question_id=q5.id, value="PHP", text="PHP"),
            models.QuestionOption(question_id=q5.id, value="GO", text="Go"),
            models.QuestionOption(question_id=q5.id, value="RUST", text="Rust"),
            models.QuestionOption(question_id=q5.id, value="PYTHON", text="Python")
        ]
        db.add_all(stack_options)
        
        # Question 6: Certificates
        q6 = models.Question(
            name="certificates",
            type="file",
            required=True,
            text="Upload any of your certificates?",
            description="You can upload multiple (.pdf)",
            file_format=".pdf",
            max_file_size=1,
            max_file_size_unit="mb",
            multiple_files=True
        )
        db.add(q6)
        
        # Commit all changes
        db.commit()
        print("Database seeded successfully with questions!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise

if __name__ == "__main__":
    seed_questions()