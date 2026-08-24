"""Create interview questions.

Revision ID: 20260820_1135
Revises: 20260820_1110
Create Date: 2026-08-20 11:35:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260820_1135"
down_revision: str | None = "20260820_1110"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INTERVIEW_QUESTIONS = [
    {
        "question": (
            "Retrieve employee names and salaries for employees in the Finance "
            "department."
        ),
        "category": "SQL",
        "topic": "Filtering and joins",
        "subtopic": "Department filter",
        "question_type": "coding",
        "difficulty": "easy",
        "answer_format": "sql",
        "expected_concepts": "SELECT, JOIN, WHERE, department filtering",
        "reference_answer": (
            "Join employees to departments on department_id, filter the department "
            "name to Finance, and select employee name and salary."
        ),
    },
    {
        "question": "Increase salaries of all IT employees by 10%.",
        "category": "SQL",
        "topic": "Updates",
        "subtopic": "Conditional update",
        "question_type": "coding",
        "difficulty": "easy",
        "answer_format": "sql",
        "expected_concepts": "UPDATE, SET, WHERE, percentage calculation",
        "reference_answer": (
            "Use UPDATE with a WHERE clause targeting IT employees and set salary "
            "to salary * 1.10."
        ),
    },
    {
        "question": "Find duplicate email addresses in a Person table.",
        "category": "SQL",
        "topic": "Aggregation",
        "subtopic": "Duplicates",
        "question_type": "coding",
        "difficulty": "easy",
        "answer_format": "sql",
        "expected_concepts": "GROUP BY, HAVING, COUNT",
        "reference_answer": (
            "Group by email and keep groups where COUNT(*) is greater than 1."
        ),
    },
    {
        "question": "Find the second highest salary.",
        "category": "SQL",
        "topic": "Ranking",
        "subtopic": "Second highest value",
        "question_type": "coding",
        "difficulty": "medium",
        "answer_format": "sql",
        "expected_concepts": "DISTINCT, ordering, window functions or OFFSET",
        "reference_answer": (
            "Use a rank or dense_rank window over distinct salaries, then return "
            "the salary ranked second."
        ),
    },
    {
        "question": "Find the third highest salary.",
        "category": "SQL",
        "topic": "Ranking",
        "subtopic": "Nth highest value",
        "question_type": "coding",
        "difficulty": "medium",
        "answer_format": "sql",
        "expected_concepts": "DENSE_RANK, DISTINCT, ordering",
        "reference_answer": (
            "Rank distinct salaries descending with DENSE_RANK and filter for rank 3."
        ),
    },
    {
        "question": "Find numbers appearing at least three times consecutively.",
        "category": "SQL",
        "topic": "Window functions",
        "subtopic": "Consecutive rows",
        "question_type": "coding",
        "difficulty": "hard",
        "answer_format": "sql",
        "expected_concepts": "LAG, LEAD, ordered rows, consecutive comparison",
        "reference_answer": (
            "Compare each row with neighboring rows using LAG and LEAD over the "
            "ordered sequence and return values where all three match."
        ),
    },
    {
        "question": "Find employees who earn more than their managers.",
        "category": "SQL",
        "topic": "Self joins",
        "subtopic": "Employee manager hierarchy",
        "question_type": "coding",
        "difficulty": "medium",
        "answer_format": "sql",
        "expected_concepts": "Self join, manager_id, salary comparison",
        "reference_answer": (
            "Join employees to the same table as managers and filter where the "
            "employee salary is greater than the manager salary."
        ),
    },
    {
        "question": (
            "Explain INNER JOIN vs LEFT JOIN vs RIGHT JOIN vs FULL JOIN and when "
            "each is useful."
        ),
        "category": "SQL",
        "topic": "Joins",
        "subtopic": "Join semantics",
        "question_type": "conceptual",
        "difficulty": "easy",
        "answer_format": "free_text",
        "expected_concepts": "Matched rows, preserved side, unmatched rows, nulls",
        "reference_answer": (
            "INNER returns matches only. LEFT preserves all rows from the left. "
            "RIGHT preserves all rows from the right. FULL preserves rows from both "
            "sides and fills missing matches with nulls."
        ),
    },
    {
        "question": "Generate an infinite Fibonacci sequence using a generator.",
        "category": "Python",
        "topic": "Generators",
        "subtopic": "Fibonacci",
        "question_type": "coding",
        "difficulty": "medium",
        "answer_format": "python",
        "expected_concepts": "yield, loop, state variables",
        "reference_answer": (
            "Keep two variables for the previous values, yield the current value, "
            "and update them inside an infinite loop."
        ),
    },
    {
        "question": "Sort a list without using sort.",
        "category": "Python",
        "topic": "Algorithms",
        "subtopic": "Sorting",
        "question_type": "coding",
        "difficulty": "medium",
        "answer_format": "python",
        "expected_concepts": "Comparison, loops, swapping, algorithm tradeoffs",
        "reference_answer": (
            "Implement a simple algorithm such as insertion sort or selection sort "
            "and explain its complexity."
        ),
    },
    {
        "question": "Check whether a string is a palindrome.",
        "category": "Python",
        "topic": "Strings",
        "subtopic": "Palindrome",
        "question_type": "coding",
        "difficulty": "easy",
        "answer_format": "python",
        "expected_concepts": "Normalization, slicing or two pointers",
        "reference_answer": (
            "Normalize the string if required and compare it to its reverse, or "
            "use two pointers from both ends."
        ),
    },
    {
        "question": "Calculate factorial.",
        "category": "Python",
        "topic": "Recursion and loops",
        "subtopic": "Factorial",
        "question_type": "coding",
        "difficulty": "easy",
        "answer_format": "python",
        "expected_concepts": "Loop or recursion, base case, input validation",
        "reference_answer": (
            "Return 1 for 0 or 1, otherwise multiply numbers from 2 through n or "
            "use recursion with a base case."
        ),
    },
    {
        "question": "Calculate word frequencies in a sentence.",
        "category": "Python",
        "topic": "Collections",
        "subtopic": "Counting",
        "question_type": "coding",
        "difficulty": "easy",
        "answer_format": "python",
        "expected_concepts": "Tokenization, dictionary or Counter",
        "reference_answer": (
            "Split normalized text into words and count with a dictionary or "
            "collections.Counter."
        ),
    },
    {
        "question": "Find minimum and maximum values in an array.",
        "category": "Python",
        "topic": "Arrays",
        "subtopic": "Min max scan",
        "question_type": "coding",
        "difficulty": "easy",
        "answer_format": "python",
        "expected_concepts": "Iteration, comparisons, empty input handling",
        "reference_answer": (
            "Initialize min and max from the first element, scan the array once, "
            "and update each value when a smaller or larger element appears."
        ),
    },
    {
        "question": "Explain RDD vs DataFrame vs Dataset.",
        "category": "Spark",
        "topic": "Spark fundamentals",
        "subtopic": "Core abstractions",
        "question_type": "conceptual",
        "difficulty": "medium",
        "answer_format": "free_text",
        "expected_concepts": "RDD, DataFrame, Dataset, schema, optimization",
        "reference_answer": (
            "RDDs are low-level distributed collections. DataFrames are structured "
            "tables optimized by Catalyst. Datasets add typed APIs in languages "
            "that support them."
        ),
    },
    {
        "question": "Explain Spark lazy evaluation and the DAG.",
        "category": "Spark",
        "topic": "Execution model",
        "subtopic": "Lazy evaluation",
        "question_type": "conceptual",
        "difficulty": "medium",
        "answer_format": "free_text",
        "expected_concepts": "Transformations, actions, DAG, optimization",
        "reference_answer": (
            "Transformations build a logical plan lazily. Actions trigger Spark to "
            "optimize the DAG and execute stages across the cluster."
        ),
    },
    {
        "question": "How would you optimize a slow PySpark or Spark job?",
        "category": "Spark",
        "topic": "Performance",
        "subtopic": "Optimization",
        "question_type": "scenario",
        "difficulty": "hard",
        "answer_format": "free_text",
        "expected_concepts": "Partitions, shuffles, joins, caching, file sizes",
        "reference_answer": (
            "Inspect the Spark UI, identify shuffles and skew, tune partitions, "
            "broadcast small tables, cache reused data, and reduce unnecessary "
            "wide transformations."
        ),
    },
    {
        "question": "How do you handle data skew or imbalanced joins?",
        "category": "Spark",
        "topic": "Performance",
        "subtopic": "Skew",
        "question_type": "scenario",
        "difficulty": "hard",
        "answer_format": "free_text",
        "expected_concepts": "Skew detection, salting, broadcast joins, repartitioning",
        "reference_answer": (
            "Find skewed keys, consider salting or splitting hot keys, broadcast "
            "small dimensions, and repartition data around useful keys."
        ),
    },
    {
        "question": "What are broadcast variables and when should they be used?",
        "category": "Spark",
        "topic": "Performance",
        "subtopic": "Broadcasting",
        "question_type": "conceptual",
        "difficulty": "medium",
        "answer_format": "free_text",
        "expected_concepts": (
            "Read-only shared data, executor memory, small lookup data"
        ),
        "reference_answer": (
            "Broadcast variables distribute read-only data to executors so tasks "
            "can use a local copy instead of repeatedly shipping it."
        ),
    },
    {
        "question": "Implement or use a UDF.",
        "category": "Spark",
        "topic": "PySpark coding",
        "subtopic": "UDF",
        "question_type": "coding",
        "difficulty": "medium",
        "answer_format": "python",
        "expected_concepts": "Function definition, udf registration, column expression",
        "reference_answer": (
            "Define a Python function, wrap it with udf and a return type, then "
            "apply it to a DataFrame column. Mention built-in functions are often "
            "faster."
        ),
    },
    {
        "question": "How do you handle duplicate records in a DataFrame?",
        "category": "Spark",
        "topic": "Data quality",
        "subtopic": "Deduplication",
        "question_type": "coding",
        "difficulty": "easy",
        "answer_format": "python",
        "expected_concepts": "dropDuplicates, subset columns, business key",
        "reference_answer": (
            "Use dropDuplicates with the appropriate subset of business-key columns "
            "and explain how you choose those keys."
        ),
    },
    {
        "question": "Filter and aggregate a large dataset.",
        "category": "Spark",
        "topic": "PySpark coding",
        "subtopic": "Filtering and aggregation",
        "question_type": "coding",
        "difficulty": "medium",
        "answer_format": "python",
        "expected_concepts": "filter, groupBy, agg, partition awareness",
        "reference_answer": (
            "Filter early to reduce data, group by the required keys, and aggregate "
            "with built-in functions."
        ),
    },
    {
        "question": "Difference between cache() and persist().",
        "category": "Spark",
        "topic": "Performance",
        "subtopic": "Caching",
        "question_type": "conceptual",
        "difficulty": "medium",
        "answer_format": "free_text",
        "expected_concepts": "Storage levels, memory, disk, reuse",
        "reference_answer": (
            "cache is a shorthand for a default storage level. persist lets you "
            "choose storage levels such as memory, disk, or serialized formats."
        ),
    },
    {
        "question": "How would you build an ETL pipeline using Azure Data Factory?",
        "category": "Azure",
        "topic": "Data Factory",
        "subtopic": "ETL design",
        "question_type": "scenario",
        "difficulty": "medium",
        "answer_format": "free_text",
        "expected_concepts": (
            "Linked services, datasets, pipelines, triggers, monitoring"
        ),
        "reference_answer": (
            "Define linked services and datasets, compose copy and transformation "
            "activities in a pipeline, schedule with triggers, and monitor runs."
        ),
    },
    {
        "question": (
            "How would you implement incremental loading using a watermark or "
            "timestamp?"
        ),
        "category": "Azure",
        "topic": "Data Engineering",
        "subtopic": "Incremental load",
        "question_type": "scenario",
        "difficulty": "medium",
        "answer_format": "free_text",
        "expected_concepts": "Watermark table, last processed timestamp, idempotency",
        "reference_answer": (
            "Store the last successful watermark, filter source records newer than "
            "that value, load them idempotently, and update the watermark only after "
            "success."
        ),
    },
    {
        "question": "Explain Azure Databricks architecture.",
        "category": "Azure",
        "topic": "Databricks",
        "subtopic": "Architecture",
        "question_type": "conceptual",
        "difficulty": "medium",
        "answer_format": "free_text",
        "expected_concepts": "Workspace, clusters, driver, workers, storage",
        "reference_answer": (
            "Describe the workspace control plane, clusters with driver and worker "
            "nodes, Spark execution, and integration with cloud storage."
        ),
    },
    {
        "question": "How do you manage schema drift in ADF?",
        "category": "Azure",
        "topic": "Data Factory",
        "subtopic": "Schema drift",
        "question_type": "scenario",
        "difficulty": "hard",
        "answer_format": "free_text",
        "expected_concepts": "Mapping, validation, drift handling, monitoring",
        "reference_answer": (
            "Use explicit mapping where possible, schema drift options where needed, "
            "validation checks, and alerts when unexpected columns or types appear."
        ),
    },
    {
        "question": (
            "How should secrets and credentials be managed securely in Azure data "
            "pipelines?"
        ),
        "category": "Azure",
        "topic": "Security",
        "subtopic": "Secrets",
        "question_type": "conceptual",
        "difficulty": "medium",
        "answer_format": "free_text",
        "expected_concepts": "Key Vault, managed identity, least privilege, rotation",
        "reference_answer": (
            "Use managed identities and Key Vault-backed secrets, avoid hard-coded "
            "credentials, apply least privilege, and rotate credentials."
        ),
    },
    {
        "question": (
            "Tell me about a project where you handled large-scale data processing."
        ),
        "category": "Behavioral",
        "topic": "Project experience",
        "subtopic": "Scale",
        "question_type": "behavioral",
        "difficulty": "medium",
        "answer_format": "star",
        "expected_concepts": "Situation, Task, Action, Result, scale, tradeoffs",
        "reference_answer": (
            "Use STAR: explain the context, the scale challenge, your concrete "
            "actions, and the measurable result."
        ),
    },
    {
        "question": "How do you handle tight client deadlines?",
        "category": "Behavioral",
        "topic": "Delivery",
        "subtopic": "Deadlines",
        "question_type": "behavioral",
        "difficulty": "easy",
        "answer_format": "star",
        "expected_concepts": "Prioritization, communication, scope, risk management",
        "reference_answer": (
            "Explain how you clarify priorities, communicate risks early, sequence "
            "work, and protect quality on the most important deliverables."
        ),
    },
    {
        "question": "Describe a situation where you improved pipeline performance.",
        "category": "Behavioral",
        "topic": "Performance",
        "subtopic": "Optimization story",
        "question_type": "behavioral",
        "difficulty": "medium",
        "answer_format": "star",
        "expected_concepts": "Baseline, diagnosis, optimization, measurable impact",
        "reference_answer": (
            "Use STAR and include the original bottleneck, your investigation, the "
            "change you made, and measurable runtime or cost improvement."
        ),
    },
    {
        "question": (
            "How do you communicate technical topics to non-technical stakeholders?"
        ),
        "category": "Behavioral",
        "topic": "Communication",
        "subtopic": "Stakeholders",
        "question_type": "behavioral",
        "difficulty": "easy",
        "answer_format": "star",
        "expected_concepts": "Audience, analogy, business impact, confirmation",
        "reference_answer": (
            "Focus on the business decision, avoid unnecessary jargon, use examples, "
            "and confirm the audience understood the tradeoffs."
        ),
    },
    {
        "question": "What would you do if a production data pipeline failed?",
        "category": "Behavioral",
        "topic": "Incident response",
        "subtopic": "Pipeline failure",
        "question_type": "scenario",
        "difficulty": "hard",
        "answer_format": "free_text",
        "expected_concepts": "Triage, rollback, communication, root cause, prevention",
        "reference_answer": (
            "Triage impact, stabilize or roll back, communicate status, preserve "
            "evidence, fix root cause, and add monitoring or tests to prevent repeat "
            "failures."
        ),
    },
]


def upgrade() -> None:
    interview_questions = op.create_table(
        "interview_questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("topic", sa.String(length=80), nullable=False),
        sa.Column("subtopic", sa.String(length=120), nullable=True),
        sa.Column("question_type", sa.String(length=20), nullable=False),
        sa.Column("difficulty", sa.String(length=20), nullable=False),
        sa.Column("answer_format", sa.String(length=20), nullable=False),
        sa.Column("expected_concepts", sa.Text(), nullable=True),
        sa.Column("reference_answer", sa.Text(), nullable=True),
        sa.Column("source", sa.String(length=160), nullable=True),
        sa.Column("source_context", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "question_type in ('coding', 'conceptual', 'scenario', 'behavioral')",
            name="ck_interview_questions_question_type",
        ),
        sa.CheckConstraint(
            "difficulty in ('easy', 'medium', 'hard')",
            name="ck_interview_questions_difficulty",
        ),
        sa.CheckConstraint(
            "answer_format in ('sql', 'python', 'free_text', 'star')",
            name="ck_interview_questions_answer_format",
        ),
    )
    op.create_index(
        "ix_interview_questions_category", "interview_questions", ["category"]
    )
    op.create_index("ix_interview_questions_topic", "interview_questions", ["topic"])
    op.create_index(
        "ix_interview_questions_question_type",
        "interview_questions",
        ["question_type"],
    )
    op.create_index(
        "ix_interview_questions_difficulty",
        "interview_questions",
        ["difficulty"],
    )
    op.bulk_insert(interview_questions, INTERVIEW_QUESTIONS)


def downgrade() -> None:
    op.drop_index("ix_interview_questions_difficulty", table_name="interview_questions")
    op.drop_index(
        "ix_interview_questions_question_type",
        table_name="interview_questions",
    )
    op.drop_index("ix_interview_questions_topic", table_name="interview_questions")
    op.drop_index("ix_interview_questions_category", table_name="interview_questions")
    op.drop_table("interview_questions")
